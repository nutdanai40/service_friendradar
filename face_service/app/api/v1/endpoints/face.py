from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from app.services.face_service import FaceRecognitionService
from app.schemas.face import (
    FaceRegistrationResponse,
    FaceVerificationResponse,
    FaceRecognitionResponse,
    UserListResponse,
    MessageResponse
)

router = APIRouter()

# Dependency to get service instance
# In a real app, this might be a singleton or injected via a more complex mechanism
# For now, we instantiate it here or use a global instance if state needs to be shared
# Since the service uses in-memory storage, we MUST use a single global instance
service = FaceRecognitionService()

@router.post("/register", response_model=FaceRegistrationResponse)
async def register(user_id: str = Form(...), file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="ไม่ได้อัปโหลดไฟล์")
    
    success = service.register_face(user_id, file.file)
    if not success:
        raise HTTPException(status_code=400, detail="ไม่พบใบหน้าในรูปภาพ กรุณาอัปโหลดรูปที่มีใบหน้าชัดเจน")
        
    return {"message": f"ลงทะเบียนผู้ใช้ {user_id} เรียบร้อยแล้ว"}

@router.post("/verify", response_model=FaceVerificationResponse)
async def verify(user_id: str = Form(...), file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="ไม่ได้อัปโหลดไฟล์")
    
    if user_id not in service.known_faces:
        raise HTTPException(status_code=404, detail=f"ไม่พบผู้ใช้ {user_id} ในระบบ")
        
    is_match = service.verify_face(user_id, file.file)
    if is_match is None:
        raise HTTPException(status_code=400, detail="ไม่พบใบหน้าในรูปภาพ กรุณาอัปโหลดรูปที่มีใบหน้าชัดเจน")
    
    return {"user_id": user_id, "verified": is_match, "message": "ยืนยันตัวตนสำเร็จ" if is_match else "ยืนยันตัวตนไม่ผ่าน"}

@router.post("/recognize", response_model=FaceRecognitionResponse)
async def recognize(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="ไม่ได้อัปโหลดไฟล์")
    
    result = service.recognize_face(file.file)
    if result is None:
        raise HTTPException(status_code=400, detail="ไม่พบใบหน้าในรูปภาพ กรุณาอัปโหลดรูปที่มีใบหน้าชัดเจน")
    
    if result:
        return {"identified": True, "user_id": result, "message": f"ระบุตัวตนได้: {result}"}
    else:
        return {"identified": False, "user_id": None, "message": "ไม่สามารถระบุตัวตนได้"}

@router.delete("/clear", response_model=MessageResponse)
def clear_all_faces():
    """ลบข้อมูลใบหน้าทั้งหมด"""
    count = len(service.known_faces)
    service.known_faces.clear()
    return {"message": f"ลบข้อมูลใบหน้าทั้งหมดแล้ว ({count} ผู้ใช้)"}

@router.delete("/clear/{user_id}", response_model=MessageResponse)
def clear_user_face(user_id: str):
    """ลบข้อมูลใบหน้าของผู้ใช้คนใดคนหนึ่ง"""
    if user_id in service.known_faces:
        del service.known_faces[user_id]
        return {"message": f"ลบข้อมูลผู้ใช้ {user_id} แล้ว"}
    else:
        raise HTTPException(status_code=404, detail=f"ไม่พบผู้ใช้ {user_id} ในระบบ")

@router.get("/users", response_model=UserListResponse)
def list_users():
    """แสดงรายชื่อผู้ใช้ทั้งหมดที่ลงทะเบียนไว้"""
    users = list(service.known_faces.keys())
    return {"total": len(users), "users": users}
