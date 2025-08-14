import re
import json
import torch
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from transformers import DonutProcessor, VisionEncoderDecoderModel
from PIL import Image
import io

class ProcessRequest(BaseModel):
    """Request model for processing documents"""
    image_paths: List[str]

class ProcessResponse(BaseModel):
    """Response model for processing results"""
    success: bool
    results: Dict[str, Any]
    message: str = ""

class DonutMCPServer:
    """Donut Document Parser MCP Server using FastAPI"""
    
    def __init__(self, model_name: str = "naver-clova-ix/donut-base-finetuned-cord-v2"):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"Loading model: {model_name}")
        self.processor = DonutProcessor.from_pretrained(model_name)
        self.model = VisionEncoderDecoderModel.from_pretrained(model_name)
        self.model.to(self.device)
        print(f"Model loaded successfully on {self.device}")
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="Donut MCP Server",
            description="Model Context Protocol server for Donut document parsing",
            version="1.0.0"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup routes
        self.setup_routes()
    
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/")
        async def root():
            return {
                "message": "Donut MCP Server is running",
                "model": self.model_name,
                "device": self.device,
                "endpoints": {
                    "health": "/health",
                    "process_file": "/process/file",
                    "process_paths": "/process/paths",
                    "batch_process": "/process/batch"
                }
            }
        
        @self.app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "model": self.model_name,
                "device": self.device,
                "cuda_available": torch.cuda.is_available()
            }
        
        @self.app.post("/process/file", response_model=ProcessResponse)
        async def process_uploaded_file(file: UploadFile = File(...)):
            """Process an uploaded image file"""
            try:
                # Validate file type
                if not file.content_type.startswith('image/'):
                    raise HTTPException(status_code=400, detail="File must be an image")
                
                # Read and process image
                image_data = await file.read()
                image = Image.open(io.BytesIO(image_data))
                
                result = self._process_image(image)
                
                return ProcessResponse(
                    success=True,
                    results={file.filename: result},
                    message="File processed successfully"
                )
                
            except Exception as e:
                return ProcessResponse(
                    success=False,
                    results={},
                    message=f"Error processing file: {str(e)}"
                )
        
        @self.app.post("/process/paths", response_model=ProcessResponse)
        async def process_by_paths(request: ProcessRequest):
            """Process images by file paths"""
            try:
                results = {}
                errors = []
                
                for image_path in request.image_paths:
                    try:
                        result = self.process_document(image_path)
                        results[image_path] = result
                    except Exception as e:
                        errors.append(f"{image_path}: {str(e)}")
                        results[image_path] = {"error": str(e)}
                
                success = len(errors) == 0
                message = "All files processed successfully" if success else f"Processed with {len(errors)} errors"
                
                return ProcessResponse(
                    success=success,
                    results=results,
                    message=message
                )
                
            except Exception as e:
                return ProcessResponse(
                    success=False,
                    results={},
                    message=f"Error processing paths: {str(e)}"
                )
        
        @self.app.post("/process/batch")
        async def batch_process_files(files: List[UploadFile] = File(...)):
            """Process multiple uploaded files in batch"""
            try:
                results = {}
                
                for file in files:
                    if not file.content_type.startswith('image/'):
                        results[file.filename] = {"error": "File must be an image"}
                        continue
                    
                    try:
                        image_data = await file.read()
                        image = Image.open(io.BytesIO(image_data))
                        result = self._process_image(image)
                        results[file.filename] = result
                    except Exception as e:
                        results[file.filename] = {"error": str(e)}
                
                return {
                    "success": True,
                    "results": results,
                    "message": f"Processed {len(files)} files"
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    
    def _process_image(self, image: Image.Image) -> Dict[str, Any]:
        """Internal method to process PIL Image object"""
        try:
            # Prepare encoder inputs
            pixel_values = self.processor(image, return_tensors="pt").pixel_values
            
            # Prepare decoder inputs
            task_prompt = "<s_cord-v2>"
            decoder_input_ids = self.processor.tokenizer(
                task_prompt, 
                add_special_tokens=False, 
                return_tensors="pt"
            ).input_ids
            
            # Generate answer
            outputs = self.model.generate(
                pixel_values.to(self.device),
                decoder_input_ids=decoder_input_ids.to(self.device),
                max_length=self.model.decoder.config.max_position_embeddings,
                early_stopping=True,
                pad_token_id=self.processor.tokenizer.pad_token_id,
                eos_token_id=self.processor.tokenizer.eos_token_id,
                use_cache=True,
                num_beams=1,
                bad_words_ids=[[self.processor.tokenizer.unk_token_id]],
                return_dict_in_generate=True,
            )
            
            # Postprocess
            sequence = self.processor.batch_decode(outputs.sequences)[0]
            sequence = sequence.replace(self.processor.tokenizer.eos_token, "").replace(
                self.processor.tokenizer.pad_token, ""
            )
            sequence = re.sub(r"<.*?>", "", sequence, count=1).strip()
            
            result = self.processor.token2json(sequence)
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    def process_document(self, image_path: str) -> Dict[str, Any]:
        """
        Process a document image from file path and return structured data
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing the parsed document information
        """
        try:
            # Load and validate image
            if not Path(image_path).exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            image = Image.open(image_path)
            return self._process_image(image)
            
        except Exception as e:
            return {"error": str(e)}
    
    def run_server(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the FastAPI server"""
        print(f"Starting Donut MCP Server on {host}:{port}")
        print(f"Model: {self.model_name}")
        print(f"Device: {self.device}")
        print(f"API Documentation: http://{host}:{port}/docs")
        
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level="info"
        )

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Donut MCP Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--model", type=str, default="naver-clova-ix/donut-base-finetuned-cord-v2", 
                       help="Model name or path")
    
    args = parser.parse_args()
    
    # Create and run server
    server = DonutMCPServer(args.model)
    server.run_server(args.host, args.port)

if __name__ == "__main__":
    main()