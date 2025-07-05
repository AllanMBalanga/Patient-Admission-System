from fastapi import APIRouter, status, HTTPException
from ..body import Province
from ..response import ProvinceResponse
from ..database import Database
from ..update import ProvincesPut, ProvincesPatch, dynamic_patch_query
from ..status_codes import validate_province_exists, validate_excluded_values
from typing import List

#provinces requests (get all/by id, post, delete, put, patch)
router = APIRouter(
    prefix="/provinces",
    tags=["Provinces"]
)

db = Database()

@router.get("/", response_model=List[ProvinceResponse])
def get_provinces():
    db.cursor.execute("SELECT * FROM provinces")
    provinces = db.cursor.fetchall()
    return [ProvinceResponse(**row) for row in provinces]


@router.post("/", response_model=ProvinceResponse, status_code=status.HTTP_201_CREATED)
def create_province(province: Province):
    try:
        db.cursor.execute("INSERT INTO provinces (name, city) VALUES (%s, %s)", (province.name, province.city))
        db.conn.commit()

        db.cursor.execute("SELECT * FROM provinces WHERE id = LAST_INSERT_ID()")
        created = db.cursor.fetchone()

        return ProvinceResponse(**created)

    except HTTPException as http_exception:
        raise http_exception
    
    except Exception:
        db.conn.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{province_id}", response_model=ProvinceResponse)
def get_province_by_id(province_id: int):
    db.cursor.execute("SELECT * FROM provinces WHERE id = %s", (province_id,))
    province = db.cursor.fetchone()
    
    return ProvinceResponse(**province)


@router.delete("/{province_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_province(province_id: int):
    try:
        db.cursor.execute("SELECT * FROM provinces WHERE id = %s", (province_id,))
        deleted_province = db.cursor.fetchone()
        validate_province_exists(deleted_province, province_id)

        db.cursor.execute("DELETE FROM provinces WHERE id = %s", (province_id,))

        db.conn.commit()
        return 

    except HTTPException as http_exception:
        raise http_exception
    
    except Exception:
        db.conn.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{province_id}", response_model=ProvinceResponse)
def put_province(province_id: int, province: ProvincesPut):
    try:
        db.cursor.execute("SELECT * FROM provinces WHERE id = %s", (province_id,))
        existing_province = db.cursor.fetchone()
        validate_province_exists(existing_province, province_id)

        db.cursor.execute("UPDATE provinces SET name = %s, city = %s WHERE id = %s", (province.name, province.city, province_id))
        db.conn.commit()
        db.cursor.execute("SELECT * FROM provinces WHERE id = %s", (province_id,))
        updated_province = db.cursor.fetchone()

        return ProvinceResponse(**updated_province)

    except HTTPException as http_exception:
        raise http_exception
    
    except Exception:
        db.conn.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/{province_id}", response_model=ProvinceResponse)
def patch_province(province_id: int, province: ProvincesPatch):
    try:
        db.cursor.execute("SELECT * FROM provinces WHERE id = %s", (province_id,))
        existing_province = db.cursor.fetchone()
        validate_province_exists(existing_province, province_id)

        excluded_values= province.dict(exclude_unset=True)
        validate_excluded_values(excluded_values)
        
        sql, values = dynamic_patch_query("provinces", excluded_values, province_id)
        db.cursor.execute(sql, values)
        db.conn.commit()

        db.cursor.execute("SELECT * FROM provinces WHERE id = %s", (province_id,))
        updated_province = db.cursor.fetchone()

        return ProvinceResponse(**updated_province)

    except HTTPException as http_exception:
        raise http_exception
    
    except Exception:
        db.conn.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")