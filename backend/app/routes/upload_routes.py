
from fastapi import UploadFile, APIRouter, File, Depends,Form, HTTPException, Query
from typing import Optional, List
import uuid
import os
import json
from sklearn.neighbors import NearestNeighbors
import uvicorn
import logging
from datetime import datetime
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import os
from dotenv import load_dotenv
from ..security import get_current_user
from mysql.connector import Error
from ..model import User
import asyncio



from ..db.database import get_db, get_database_connection
from ..tables import ImageMetadata, ImageResponse,BatchUploadResponse,BatchImageMetadata, UpdateCategoryRequest
from ..security import get_current_user
from ..utils.image_processing import process_single_image



from ..services.occasion_weather_outfits import WeatherService, SmartOutfitRecommender, WeatherOccasionRequest


UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB per file
MAX_FILES_PER_REQUEST = 20
MIN_FILES_PER_REQUEST = 1


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

executor = ThreadPoolExecutor(max_workers=4)

router = APIRouter()



@router.post("/upload-image", response_model=ImageResponse)
async def upload_single_image(
    file: UploadFile = File(...),
    style: Optional[str] = Form(None),
    occasion: Optional[str] = Form(None),
    season: Optional[str] = Form(None),
    temperature_min: Optional[int] = Form(None),
    temperature_max: Optional[int] = Form(None),
    gender: Optional[str] = Form(None),
    material: Optional[str] = Form(None),
    pattern: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """Upload and process a single image (legacy endpoint)"""
    try:
        # Validate file
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Check file size
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")
        
        # Process the image
        extra_metadata = {
            "style": style,
            "occasion": occasion.split(',') if occasion else None,
            "season": season.split(',') if season else None,
            "temperature_range": {"min": temperature_min, "max": temperature_max} if temperature_min is not None and temperature_max is not None else None,
            "gender": gender,
            "material": material,
            "pattern": pattern,
            "user_id":  current_user.id
        }
        file_data = (contents, file.filename, file.filename)
        result = process_single_image(file_data, extra_metadata=extra_metadata)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        metadata = result["metadata"]
        
        # Store in database
        try:
            connection = get_database_connection()
            cursor = connection.cursor()
            
            insert_query = """
                INSERT INTO images (
                    id, filename, original_name, file_size, image_width, image_height,
                    dominant_color, color_palette, resnet_features, opencv_features, 
                    upload_date, batch_id, category, clothing_part, background_removed, foreground_pixel_count,
                    style, occasion, season, temperature_range, gender, material, pattern, user_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s)
                """
            
            values = (
                metadata["id"],
                metadata["filename"],
                metadata["original_name"],
                metadata["file_size"],
                metadata["image_width"],
                metadata["image_height"],
                metadata["dominant_color"],
                json.dumps(metadata["color_palette"]),
                json.dumps(metadata["resnet_features"]),
                json.dumps(metadata["opencv_features"]),
                datetime.now(),
                metadata["batch_id"],
                metadata["category"],
                metadata["clothing_part"],
                metadata.get("background_removed", False),
                metadata.get("foreground_pixel_count", 0),
                metadata.get("style"),
                json.dumps(metadata.get("occasion")),
                json.dumps(metadata.get("season")),
                json.dumps(metadata.get("temperature_range")),
                metadata.get("gender"),
                metadata.get("material"),
                metadata.get("pattern"),
                metadata.get("user_id")
            )
                    
            cursor.execute(insert_query, values)
            connection.commit()
            
            logger.info(f"Successfully stored image metadata in database: {metadata['id']}")
            
        except Error as e:
            logger.error(f"Error storing in database: {str(e)}")
            # Clean up file
            if os.path.exists(result["filepath"]):
                os.remove(result["filepath"])
            raise HTTPException(status_code=500, detail="Error storing image metadata")
        
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
        
        return ImageResponse(
            message="Image uploaded and processed successfully",
            image_id=metadata["id"],
            image_url=f"http://127.0.0.1:8000/uploads/{metadata['filename']}",
            metadata=ImageMetadata(**metadata)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload_single_image: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")



@router.get("/recommend/similar/{image_id}")
def recommend_similar(image_id: str, top_k: int = 5, current_user: User = Depends(get_current_user)):
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    # 1️⃣ Fetch the query image feature and category
    cursor.execute("SELECT category, resnet_features FROM images WHERE id = %s AND user_id = %s", (image_id, current_user.id))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Image not found or you do not own it.")

    category = row['category']
    query_vec = np.array(json.loads(row['resnet_features']), dtype=np.float32)

    # 2️⃣ Fetch all metadata and features for this category
    cursor.execute("SELECT * FROM images WHERE category = %s AND user_id = %s", (category, current_user.id))
    metadata_rows = cursor.fetchall()

    exclude_keys = {"resnet_features", "opencv_features"}
    BASE_URL = "http://127.0.0.1:8000/uploads/"

    metadata_map = {}
    for r in metadata_rows:
        meta = {k: v for k, v in r.items() if k not in exclude_keys}
        if 'filename' in meta and meta['filename']:
            meta['image_url'] = BASE_URL + meta['filename']
        metadata_map[r['id']] = meta


    # 3️⃣ Fetch their resnet_features separately
    cursor.execute("SELECT id, resnet_features FROM images WHERE category = %s", (category,))
    rows = cursor.fetchall()

    ids = []
    features = []

    for r in rows:
        ids.append(r['id'])
        vec = np.array(json.loads(r['resnet_features']), dtype=np.float32)
        features.append(vec)

    if len(features) < top_k:
        raise HTTPException(status_code=400, detail="Not enough clothes in this category to recommend.")

    features = np.vstack(features)

    # 4️⃣ Build KNN on-the-fly
    knn = NearestNeighbors(n_neighbors=min(top_k + 1, len(features)), metric='euclidean')
    knn.fit(features)

    # 5️⃣ Find neighbors
    dists, idxs = knn.kneighbors([query_vec])

    # 6️⃣ Prepare response (exclude self, exclude resnet_features)
    recommendations = []
    for i in idxs[0]:
        if ids[i] != image_id:
            meta = metadata_map.get(ids[i])
            if meta:
                recommendations.append(meta)
        if len(recommendations) >= top_k:
            break

    return {
        "query_image_id": image_id,
        "category": category,
        "recommendations": recommendations
    }


@router.post("/upload-images", response_model=BatchUploadResponse)
async def upload_multiple_images(
    files: List[UploadFile] = File(...),
    metadatas: Optional[str] = Form(None), # Expecting a JSON string
    current_user: User = Depends(get_current_user)
):
    """Upload and process multiple images (1-20 images)"""
    start_time = datetime.now()
    
    try:
        # Validate number of files
        if len(files) < MIN_FILES_PER_REQUEST:
            raise HTTPException(status_code=400, detail=f"Must upload at least {MIN_FILES_PER_REQUEST} file")
        
        if len(files) > MAX_FILES_PER_REQUEST:
            raise HTTPException(status_code=400, detail=f"Cannot upload more than {MAX_FILES_PER_REQUEST} files at once")
        
        # Generate batch ID
        batch_id = str(uuid.uuid4())
        
        # Prepare file data for processing
        file_data_list = []
        for file in files:
            # Validate file type
            if not file.content_type or not file.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail=f"File {file.filename} must be an image")
            
            # Check file size
            contents = await file.read()
            if len(contents) > MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail=f"File {file.filename} is too large")
            
            file_data_list.append((contents, file.filename, file.filename))
        
        # Process images in parallel
        logger.info(f"Processing {len(file_data_list)} images in batch {batch_id}")
        
        # Parse metadatas if provided
        metadata_list = json.loads(metadatas) if metadatas else [{}] * len(files)

        # Use ThreadPoolExecutor for parallel processing
        loop = asyncio.get_event_loop()
        processing_tasks = []
        
        for i, file_data in enumerate(file_data_list):
            extra_metadata = metadata_list[i] if i < len(metadata_list) else {}
            extra_metadata['user_id'] = current_user.id
            task = loop.run_in_executor(executor, process_single_image, file_data, batch_id, extra_metadata)
            processing_tasks.append(task)
        
        # Wait for all processing to complete
        processing_results = await asyncio.gather(*processing_tasks)
        
        # Separate successful and failed results
        successful_results = [r for r in processing_results if r["success"]]
        failed_results = [r for r in processing_results if not r["success"]]
        
        # Store successful results in database
        stored_results = []
        if successful_results:
            try:
                connection = get_database_connection()
                cursor = connection.cursor()
                
                # Prepare batch insert
                insert_query = """
                INSERT INTO images (
                    id, filename, original_name, file_size, image_width, image_height,
                    dominant_color, color_palette, resnet_features, opencv_features, upload_date, batch_id, category,
                    clothing_part,style, occasion, season, temperature_range, gender, material, pattern, user_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                values_list = []
                for result in successful_results:
                    metadata = result["metadata"]
                    values = (
                        metadata["id"],
                        metadata["filename"],
                        metadata["original_name"],
                        metadata["file_size"],
                        metadata["image_width"],
                        metadata["image_height"],
                        metadata["dominant_color"],
                        json.dumps(metadata["color_palette"]),
                        json.dumps(metadata["resnet_features"]),
                        json.dumps(metadata["opencv_features"]),
                        datetime.now(),
                        batch_id,
                        metadata["category"],
                         metadata["clothing_part"],
                        metadata.get("style"),
                        json.dumps(metadata.get("occasion")),
                        json.dumps(metadata.get("season")),
                        json.dumps(metadata.get("temperature_range")),
                        metadata.get("gender"),
                        metadata.get("material"),
                        metadata.get("pattern"),
                        metadata.get("user_id")
                    )
                    values_list.append(values)
                
                # Execute batch insert
                cursor.executemany(insert_query, values_list)
                
                # Store batch metadata
                processing_time = (datetime.now() - start_time).total_seconds()
                batch_insert_query = """
                INSERT INTO batch_uploads (
                    batch_id, total_images, successful_images, failed_images, upload_date, processing_time
                ) VALUES (%s, %s, %s, %s, %s, %s)
                """
                batch_values = (
                    batch_id,
                    len(files),
                    len(successful_results),
                    len(failed_results),
                    datetime.now(),
                    processing_time
                )
                cursor.execute(batch_insert_query, batch_values)
                
                connection.commit()
                
                # Prepare successful results for response
                for result in successful_results:
                    metadata = result["metadata"]
                    stored_results.append({
                        "success": True,
                        "image_id": metadata["id"],
                        "filename": metadata["original_name"],
                        "image_url": f"http://127.0.0.1:8000/uploads/{metadata['filename']}",
                        "file_size": metadata["file_size"],
                        "dimensions": f"{metadata['image_width']}x{metadata['image_height']}",
                        "dominant_color": metadata["dominant_color"]
                    })
                
                logger.info(f"Successfully stored {len(successful_results)} images in batch {batch_id}")
                
            except Error as e:
                logger.error(f"Error storing batch in database: {str(e)}")
                # Clean up files on database error
                for result in successful_results:
                    if os.path.exists(result["filepath"]):
                        os.remove(result["filepath"])
                raise HTTPException(status_code=500, detail="Error storing image metadata")
            
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        
        # Add failed results to response
        for result in failed_results:
            stored_results.append({
                "success": False,
                "filename": result["original_name"],
                "error": result["error"]
            })
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return BatchUploadResponse(
            message=f"Batch upload completed. {len(successful_results)} successful, {len(failed_results)} failed.",
            total_images=len(files),
            successful_uploads=len(successful_results),
            failed_uploads=len(failed_results),
            batch_id=batch_id,
            results=stored_results,
            processing_time=processing_time
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload_multiple_images: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/batches")
async def get_batches(
    limit: Optional[int] = Query(10, description="Number of batches to return"),
    offset: Optional[int] = Query(0, description="Offset for pagination"),
    current_user: User = Depends(get_current_user)
):
    """Get list of batch uploads"""
    try:
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT b.* FROM batch_uploads b
        JOIN images i ON b.batch_id = i.batch_id
        WHERE i.user_id = %s
        GROUP BY b.batch_id
        ORDER BY b.created_at DESC
        LIMIT %s OFFSET %s
        """
        
        cursor.execute(query, (current_user.id, limit, offset))
        batches = cursor.fetchall()
        
        return {
            "count": len(batches),
            "batches": batches
        }
    
    except Error as e:
        logger.error(f"Error retrieving batches: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving batches")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@router.post("/update-category")
async def update_category(data: UpdateCategoryRequest,current_user: User = Depends(get_current_user)):
    """Update the category of an image"""
    try:
        connection = get_database_connection()
        cursor = connection.cursor()

        update_query = """
        UPDATE images
        SET category = %s, category_confirmed = TRUE
        WHERE id = %s AND user_id = %s
        """
        cursor.execute(update_query, (data.new_category, data.image_id, current_user.id))
        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Image not found or not owned by you")

        return {"message": "Category updated successfully"}

    except Error as e:
        logger.error(f"Error updating category: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating category")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@router.get("/batches/{batch_id}")
async def get_batch_images(batch_id: str, current_user: User = Depends(get_current_user)):
    """Get all images from a specific batch"""
    try:
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)

        # Get batch info and check ownership
        batch_query = """
            SELECT b.* FROM batch_uploads b
            JOIN (SELECT DISTINCT batch_id FROM images WHERE user_id = %s) AS user_images
            ON b.batch_id = user_images.batch_id
            WHERE b.batch_id = %s
        """
        cursor.execute(batch_query, (current_user.id, batch_id))
        batch_info = cursor.fetchone()

        if not batch_info:
            raise HTTPException(status_code=404, detail="Batch not found or you do not have access")

        # Get images in batch
        images_query = """
        SELECT id, filename, original_name, file_size, image_width, image_height,
               dominant_color, color_palette, upload_date
        FROM images 
        WHERE batch_id = %s AND user_id = %s
        ORDER BY created_at
        """
        
        cursor.execute(images_query, (batch_id, current_user.id))
        images = cursor.fetchall()
        
        # Add image URLs and parse JSON
        for image in images:
            image["image_url"] = f"http://127.0.0.1:8000/uploads/{image['filename']}"
            image["color_palette"] = json.loads(image["color_palette"])
        
        return {
            "batch_info": batch_info,
            "images": images
        }
    
    except Error as e:
        logger.error(f"Error retrieving batch images: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving batch images")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@router.get("/images")
async def get_images(
    limit: Optional[int] = Query(10, description="Number of images to return"),
    offset: Optional[int] = Query(0, description="Offset for pagination"),
    batch_id: Optional[str] = Query(None, description="Filter by batch ID"),
    current_user: User = Depends(get_current_user)
):
    """Get list of uploaded images"""
    try:
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        
        base_query = """
        SELECT id, filename, original_name, file_size, image_width, image_height,
               dominant_color, color_palette, upload_date, batch_id, category,clothing_part, 
               style, occasion, season, temperature_range, gender, material, pattern,
               created_at
        FROM images
        WHERE user_id = %s
        """
        params = [current_user.id]

        if batch_id:
            base_query += " AND batch_id = %s"
            params.append(batch_id)

        query = base_query + " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cursor.execute(query, params)
        
        images = cursor.fetchall()
        
        # Add image URLs
        for image in images:
            image["image_url"] = f"http://127.0.0.1:8000/uploads/{image['filename']}"
            image["color_palette"] = json.loads(image["color_palette"])
        
        return {
            "count": len(images),
            "images": images
        }
    
    except Error as e:
        logger.error(f"Error retrieving images: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving images")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@router.get("/images/{image_id}")
async def get_image(image_id: str, current_user: User = Depends(get_current_user)):
    """Get specific image by ID"""
    try:
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT * FROM images WHERE id = %s AND user_id = %s
        """
        
        cursor.execute(query, (image_id, current_user.id))
        image = cursor.fetchone()
        
        if not image:
            raise HTTPException(status_code=404, detail="Image not found or you do not own it")
        
        # Parse JSON fields
        image["color_palette"] = json.loads(image["color_palette"])
        image["resnet_features"] = json.loads(image["resnet_features"])
        image["opencv_features"] = json.loads(image["opencv_features"])
        image["image_url"] = f"http://127.0.0.1:8000/uploads/{image['filename']}"
        
        return image
    
    except Error as e:
        logger.error(f"Error retrieving image: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving image")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@router.delete("/images/{image_id}")
async def delete_image(image_id: str, current_user: User = Depends(get_current_user)):
    """Delete an image"""
    try:
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get image info first
        cursor.execute("SELECT filename FROM images WHERE id = %s AND user_id = %s", (image_id, current_user.id))
        image = cursor.fetchone()
        
        if not image:
            raise HTTPException(status_code=404, detail="Image not found or you do not own it")
        
        # Delete from database
        cursor.execute("DELETE FROM images WHERE id = %s AND user_id = %s", (image_id, current_user.id))
        connection.commit()
        
        # Delete file
        filepath = os.path.join(UPLOAD_DIR, image["filename"])
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return {"message": "Image deleted successfully", "image_id": image_id}
    
    except Error as e:
        logger.error(f"Error deleting image: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting image")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@router.delete("/batches/{batch_id}")
async def delete_batch(batch_id: str, current_user: User = Depends(get_current_user)):
    """Delete an entire batch of images"""
    try:
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get all images in the batch and check ownership
        cursor.execute("SELECT filename FROM images WHERE batch_id = %s AND user_id = %s", (batch_id, current_user.id))
        images = cursor.fetchall()
        
        if not images:
            raise HTTPException(status_code=404, detail="Batch not found or you do not have access")
        
        # Delete images from database
        cursor.execute("DELETE FROM images WHERE batch_id = %s AND user_id = %s", (batch_id, current_user.id))
        
        # Delete batch record
        cursor.execute("DELETE FROM batch_uploads WHERE batch_id = %s", (batch_id,))
        
        connection.commit()
        
        # Delete files from disk
        deleted_files = 0
        for image in images:
            filepath = os.path.join(UPLOAD_DIR, image["filename"])
            if os.path.exists(filepath):
                os.remove(filepath)
                deleted_files += 1
        
        return {
            "message": f"Batch deleted successfully. Removed {len(images)} images from database and {deleted_files} files from disk.",
            "batch_id": batch_id,
            "deleted_images": len(images)
        }
    
    except Error as e:
        logger.error(f"Error deleting batch: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting batch")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@router.get("/analytics")
async def get_analytics(current_user: User = Depends(get_current_user)):
    """Get analytics about uploaded images"""
    if not current_user.role == "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    try:
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get basic statistics
        cursor.execute("SELECT COUNT(*) as total_images FROM images")
        total_images = cursor.fetchone()["total_images"]
        
        cursor.execute("SELECT SUM(file_size) as total_size FROM images")
        total_size = cursor.fetchone()["total_size"] or 0
        
        cursor.execute("SELECT AVG(image_width) as avg_width, AVG(image_height) as avg_height FROM images")
        avg_dimensions = cursor.fetchone()
        
        # Get batch statistics
        cursor.execute("SELECT COUNT(*) as total_batches FROM batch_uploads")
        total_batches = cursor.fetchone()["total_batches"]
        
        cursor.execute("SELECT AVG(processing_time) as avg_processing_time FROM batch_uploads")
        avg_processing_time = cursor.fetchone()["avg_processing_time"] or 0
        
        cursor.execute("SELECT AVG(total_images) as avg_batch_size FROM batch_uploads")
        avg_batch_size = cursor.fetchone()["avg_batch_size"] or 0
        
        # Get color distribution
        cursor.execute("SELECT dominant_color, COUNT(*) as count FROM images GROUP BY dominant_color ORDER BY count DESC LIMIT 10")
        color_distribution = cursor.fetchall()
        
        # Get category distribution
        cursor.execute("SELECT category, COUNT(*) as count FROM images GROUP BY category ORDER BY count DESC")
        category_distribution = cursor.fetchall()

        # Get style distribution
        cursor.execute("SELECT style, COUNT(*) as count FROM images GROUP BY style ORDER BY count DESC")
        style_distribution = cursor.fetchall()

        # Get season distribution
        cursor.execute("SELECT season, COUNT(*) as count FROM images GROUP BY season ORDER BY count DESC")
        season_distribution = cursor.fetchall()
        
        # Get recent batch activity
        cursor.execute("""
            SELECT batch_id, total_images, successful_images, failed_images, upload_date, processing_time
            FROM batch_uploads 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        recent_batches = cursor.fetchall()
        
        # Get upload trends (last 30 days)
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM images 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """)
        upload_trends = cursor.fetchall()
        
        return {
            "total_images": total_images,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "average_dimensions": {
                "width": round(avg_dimensions["avg_width"] or 0, 2),
                "height": round(avg_dimensions["avg_height"] or 0, 2)
            },
            "batch_statistics": {
                "total_batches": total_batches,
                "average_processing_time": round(avg_processing_time, 2),
                "average_batch_size": round(avg_batch_size, 2)
            },
            "color_distribution": color_distribution,
            "category_distribution": category_distribution,
            "style_distribution": style_distribution,
            "season_distribution": season_distribution,
            "recent_batches": recent_batches,
            "upload_trends": upload_trends
        }
    
    except Error as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving analytics")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@router.get("/search")
async def search_images(
    color: Optional[str] = Query(None, description="Search by dominant color (hex format)"),
    min_width: Optional[int] = Query(None, description="Minimum image width"),
    max_width: Optional[int] = Query(None, description="Maximum image width"),
    min_height: Optional[int] = Query(None, description="Minimum image height"),
    max_height: Optional[int] = Query(None, description="Maximum image height"),
    batch_id: Optional[str] = Query(None, description="Filter by batch ID"),
    limit: Optional[int] = Query(10, description="Number of results to return"),
    offset: Optional[int] = Query(0, description="Offset for pagination"),
    current_user: User = Depends(get_current_user)
):
    """Search images with various filters"""
    try:
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Build dynamic query
        where_conditions = ["user_id = %s"]
        params = [current_user.id]
        
        if color:
            where_conditions.append("dominant_color = %s")
            params.append(color)
        
        if min_width:
            where_conditions.append("image_width >= %s")
            params.append(min_width)
        
        if max_width:
            where_conditions.append("image_width <= %s")
            params.append(max_width)
        
        if min_height:
            where_conditions.append("image_height >= %s")
            params.append(min_height)
        
        if max_height:
            where_conditions.append("image_height <= %s")
            params.append(max_height)
        
        if batch_id:
            where_conditions.append("batch_id = %s")
            params.append(batch_id)
        
        # Construct query
        base_query = """
        SELECT id, filename, original_name, file_size, image_width, image_height,
               dominant_color, color_palette, upload_date, batch_id, created_at
        FROM images
        """
        
        query = base_query + " WHERE " + " AND ".join(where_conditions)
        
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        images = cursor.fetchall()
        
        # Add image URLs and parse JSON
        for image in images:
            image["image_url"] = f"http://0.0.0.0:8000/uploads/{image['filename']}"
            image["color_palette"] = json.loads(image["color_palette"])
        
        return {
            "count": len(images),
            "images": images,
            "filters_applied": {
                "color": color,
                "min_width": min_width,
                "max_width": max_width,
                "min_height": min_height,
                "max_height": max_height,
                "batch_id": batch_id
            }
        }
    
    except Error as e:
        logger.error(f"Error searching images: {str(e)}")
        raise HTTPException(status_code=500, detail="Error searching images")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()




@router.get("/occasion-weather")
def recommend_outfits(request: WeatherOccasionRequest):
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    weather_service = WeatherService(api_key=api_key)
    weather = weather_service.get_current_weather(request.city, request.country_code)

    wardrobe_items = request.wardrobe_items # Fetch user's uploaded clothes
    recommender = SmartOutfitRecommender(weather_service)
    recommender.load_wardrobe(wardrobe_items)

    recommendations = recommender.generate_outfit_combinations(weather, request.occasion)

    results = []
    for outfit in recommendations:
        results.append({
            "items": [{
                "id": item.id,
                "filename": item.filename,
                "category": item.category
            } for item in outfit.items],
            "score": outfit.overall_score()
        })

    return {"recommendations": results}
