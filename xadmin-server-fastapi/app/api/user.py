"""
用户管理API路由
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import (
    get_current_active_user, get_current_superuser,
    require_permission, require_roles
)
from app.schemas.base import (
    BaseResponse, ListResponse, PaginationParams, 
    BatchDeleteRequest, ChoicesResponse, SearchFieldsResponse,
    SearchColumnsResponse, ColumnInfo, FieldInfo, ChoiceItem
)
from app.schemas.user import (
    UserProfile, UserCreate, UserUpdate, UserPasswordUpdate, 
    UserListParams, UserInfoUpdate, 
    SearchUserResult, SearchRoleResult, SearchDeptResult
)
from app.schemas.auth import UserInfoResponse, UserInfoDetailResponse
from app.services.user import UserService
from app.services.role import RoleService
from app.services.dept import DeptService
from app.models.user import UserInfo
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# 用户信息相关接口（个人）
@router.get("/userinfo/", response_model=BaseResponse[UserInfoResponse])
async def get_user_info(
    current_user: UserInfo = Depends(get_current_active_user)
):
    """获取当前用户信息"""
    # 通过 getattr 安全地获取属性值，避免类型检查问题
    user_info = UserInfoResponse(
        username=getattr(current_user, 'username'),
        nickname=getattr(current_user, 'nickname', None),
        avatar=getattr(current_user, 'avatar', None),
        email=getattr(current_user, 'email', None),
        phone=getattr(current_user, 'phone', None),
        gender=getattr(current_user, 'gender', 0),
        last_login=getattr(current_user, 'last_login', None),
        date_joined=getattr(current_user, 'date_joined'),
        pk=getattr(current_user, 'id'),
        unread_message_count=0,  # TODO: 实现消息计数
        is_active=getattr(current_user, 'is_active', True),
        roles=[getattr(role, 'name') for role in current_user.roles if getattr(role, 'is_active', True)]
    )
    
    # 添加choices_dict以保持与Django一致
    response_data = {
        "data": user_info,
        "choices_dict": [
            {"value": 0, "label": "未知"},
            {"value": 1, "label": "男"},
            {"value": 2, "label": "女"}
        ]
    }
    
    return BaseResponse(
        code=1000,
        detail="success",
        **response_data
    )


@router.put("/userinfo/", response_model=BaseResponse[UserInfoResponse])
@router.patch("/userinfo/", response_model=BaseResponse[UserInfoResponse])
async def update_user_info(
    user_data: UserInfoUpdate,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user)
):
    """更新当前用户信息"""
    user_service = UserService(db)
    
    # 检查邮箱是否已存在
    if user_data.email and user_service.check_email_exists(user_data.email, getattr(current_user, 'id')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被其他用户使用"
        )
    
    # 检查手机号是否已存在
    if user_data.phone and user_service.check_phone_exists(user_data.phone, getattr(current_user, 'id')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号已被其他用户使用"
        )
    
    # 更新用户信息
    updated_user = user_service.update_user(getattr(current_user, 'id'), user_data.dict(exclude_unset=True))
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户信息失败"
        )
    
    user_info = UserInfoResponse(
        username=getattr(updated_user, 'username'),
        nickname=getattr(updated_user, 'nickname', None),
        avatar=getattr(updated_user, 'avatar', None),
        email=getattr(updated_user, 'email', None),
        phone=getattr(updated_user, 'phone', None),
        gender=getattr(updated_user, 'gender', 0),
        last_login=getattr(updated_user, 'last_login', None),
        date_joined=getattr(updated_user, 'date_joined'),
        pk=getattr(updated_user, 'id'),
        unread_message_count=0,
        is_active=getattr(updated_user, 'is_active', True),
        roles=[getattr(role, 'name') for role in updated_user.roles if getattr(role, 'is_active', True)]
    )
    
    return BaseResponse(
        code=1000,
        detail="用户信息更新成功",
        data=user_info
    )


# 用户管理接口（管理员）
@router.get("/user", response_model=ListResponse[List[UserProfile]])
async def get_user_list(
    params: UserListParams = Depends(),
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("user:read"))
):
    """获取用户列表"""
    user_service = UserService(db)
    
    filters = {}
    if params.search:
        filters['search'] = params.search
    if params.is_active is not None:
        filters['is_active'] = params.is_active
    if params.dept_id:
        filters['dept_id'] = params.dept_id
    if params.role_id:
        filters['role_id'] = params.role_id
    
    result = user_service.get_user_list(params, filters)
    
    # 转换为响应格式
    user_profiles = []
    for user in result['results']:
        # 安全地处理可能为None的关联对象
        dept_name = None
        dept_obj = getattr(user, 'dept', None)
        if dept_obj is not None:
            dept_name = getattr(dept_obj, 'name', None)
            
        role_names = []
        roles_obj = getattr(user, 'roles', None)
        if roles_obj is not None:
            role_names = [getattr(role, 'name') for role in roles_obj if getattr(role, 'is_active', True)]
        
        profile = UserProfile(
            id=getattr(user, 'id'),
            username=getattr(user, 'username'),
            email=getattr(user, 'email', None),
            phone=getattr(user, 'phone', None),
            nickname=getattr(user, 'nickname', None),
            gender=getattr(user, 'gender', 0),
            is_active=getattr(user, 'is_active', True),
            is_staff=getattr(user, 'is_staff', False),
            avatar=getattr(user, 'avatar', None),
            last_login=getattr(user, 'last_login', None),
            date_joined=getattr(user, 'date_joined'),
            is_superuser=getattr(user, 'is_superuser', False),
            created_at=getattr(user, 'created_at'),
            updated_at=getattr(user, 'updated_at'),
            dept_name=dept_name,
            role_names=role_names
        )
        user_profiles.append(profile)
    
    return ListResponse(
        code=1000,
        detail="success",
        data={
            "results": user_profiles,
            "total": result['total'],
            "page": result['page'],
            "size": result['size'],
            "pages": result['pages']
        }
    )


@router.post("/user", response_model=BaseResponse[UserProfile])
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("user:create"))
):
    """创建用户"""
    user_service = UserService(db)
    
    # 检查用户名是否已存在
    if user_service.check_username_exists(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if user_data.email and user_service.check_email_exists(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在"
        )
    
    # 检查手机号是否已存在
    if user_data.phone and user_service.check_phone_exists(user_data.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号已存在"
        )
    
    # 创建用户
    user_dict = user_data.dict(exclude={'role_ids'})
    if not user_dict.get('nickname'):
        user_dict['nickname'] = user_dict['username']
    
    user = user_service.create_user(user_dict)
    
    # 分配角色
    if user_data.role_ids:
        user_service.assign_roles(getattr(user, 'id'), user_data.role_ids)
        # 重新加载用户信息
        user = user_service.get_by_id(getattr(user, 'id'))
    
    # 安全地处理可能为None的关联对象
    dept_name = None
    dept_obj = getattr(user, 'dept', None)
    if dept_obj is not None:
        dept_name = getattr(dept_obj, 'name', None)
        
    role_names = []
    roles_obj = getattr(user, 'roles', None)
    if roles_obj is not None:
        role_names = [getattr(role, 'name') for role in roles_obj if getattr(role, 'is_active', True)]
    
    profile = UserProfile(
        id=getattr(user, 'id'),
        username=getattr(user, 'username'),
        email=getattr(user, 'email', None),
        phone=getattr(user, 'phone', None),
        nickname=getattr(user, 'nickname', None),
        gender=getattr(user, 'gender', 0),
        is_active=getattr(user, 'is_active', True),
        is_staff=getattr(user, 'is_staff', False),
        avatar=getattr(user, 'avatar', None),
        last_login=getattr(user, 'last_login', None),
        date_joined=getattr(user, 'date_joined'),
        is_superuser=getattr(user, 'is_superuser', False),
        created_at=getattr(user, 'created_at'),
        updated_at=getattr(user, 'updated_at'),
        dept_name=dept_name,
        role_names=role_names
    )
    
    return BaseResponse(
        code=1000,
        detail="用户创建成功",
        data=profile
    )


@router.put("/user/{user_id}", response_model=BaseResponse[UserProfile])
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("user:update"))
):
    """更新用户"""
    user_service = UserService(db)
    
    # 检查用户是否存在
    user = user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查邮箱是否已存在
    if user_data.email and user_service.check_email_exists(user_data.email, getattr(user, 'id')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被其他用户使用"
        )
    
    # 检查手机号是否已存在
    if user_data.phone and user_service.check_phone_exists(user_data.phone, getattr(user, 'id')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号已被其他用户使用"
        )
    
    # 更新用户信息
    update_dict = user_data.dict(exclude={'role_ids'}, exclude_unset=True)
    updated_user = user_service.update_user(user_id, update_dict)
    
    # 分配角色
    if user_data.role_ids is not None:
        user_service.assign_roles(getattr(updated_user, 'id'), user_data.role_ids)
        # 重新加载用户信息
        updated_user = user_service.get_by_id(getattr(updated_user, 'id'))
    
    # 安全地处理可能为None的关联对象
    dept_name = None
    dept_obj = getattr(updated_user, 'dept', None)
    if dept_obj is not None:
        dept_name = getattr(dept_obj, 'name', None)
        
    role_names = []
    roles_obj = getattr(updated_user, 'roles', None)
    if roles_obj is not None:
        role_names = [getattr(role, 'name') for role in roles_obj if getattr(role, 'is_active', True)]
    
    profile = UserProfile(
        id=getattr(updated_user, 'id'),
        username=getattr(updated_user, 'username'),
        email=getattr(updated_user, 'email', None),
        phone=getattr(updated_user, 'phone', None),
        nickname=getattr(updated_user, 'nickname', None),
        gender=getattr(updated_user, 'gender', 0),
        is_active=getattr(updated_user, 'is_active', True),
        is_staff=getattr(updated_user, 'is_staff', False),
        avatar=getattr(updated_user, 'avatar', None),
        last_login=getattr(updated_user, 'last_login', None),
        date_joined=getattr(updated_user, 'date_joined'),
        is_superuser=getattr(updated_user, 'is_superuser', False),
        created_at=getattr(updated_user, 'created_at'),
        updated_at=getattr(updated_user, 'updated_at'),
        dept_name=dept_name,
        role_names=role_names
    )
    
    return BaseResponse(
        code=1000,
        detail="用户更新成功",
        data=profile
    )


@router.delete("/user/{user_id}", response_model=BaseResponse[None])
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("user:delete"))
):
    """删除用户"""
    # 不能删除自己
    if user_id == getattr(current_user, 'id'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )
    
    user_service = UserService(db)
    success = user_service.delete_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return BaseResponse(
        code=1000,
        detail="用户删除成功",
        data=None
    )


@router.post("/user/batch-delete", response_model=BaseResponse[None])
async def batch_delete_users(
    request: BatchDeleteRequest,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(require_permission("user:delete"))
):
    """批量删除用户"""
    # 不能删除自己
    if getattr(current_user, 'id') in request.pks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )
    
    user_service = UserService(db)
    deleted_count = 0
    
    for user_id in request.pks:
        if user_service.delete_user(user_id):
            deleted_count += 1
    
    return BaseResponse(
        code=1000,
        detail=f"成功删除 {deleted_count} 个用户",
        data=None
    )


# 搜索接口
@router.get("/search/user", response_model=ListResponse[List[SearchUserResult]])
async def search_users(
    search: str = Query(..., description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user)
):
    """搜索用户"""
    user_service = UserService(db)
    
    params = PaginationParams(page=page, size=size, ordering=None)
    filters = {'search': search}
    
    result = user_service.get_user_list(params, filters)
    
    search_results = []
    for user in result['results']:
        # 安全地处理可能为None的关联对象
        dept_name = None
        if user.dept is not None:
            dept_name = getattr(user.dept, 'name', None)
        
        search_result = SearchUserResult(
            id=getattr(user, 'id'),
            username=getattr(user, 'username'),
            nickname=getattr(user, 'nickname', None),
            avatar=getattr(user, 'avatar', None),
            dept_name=dept_name
        )
        search_results.append(search_result)
    
    return ListResponse(
        code=1000,
        detail="success",
        data={
            "results": search_results,
            "total": result['total'],
            "page": result['page'],
            "size": result['size'],
            "pages": result['pages']
        }
    )


# 获取选择项
@router.get("/user/choices", response_model=ChoicesResponse)
async def get_user_choices(
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_active_user)
):
    """获取用户相关选择项"""
    return ChoicesResponse(
        code=1000,
        detail="success",
        data={
            "gender": [
                ChoiceItem(label="未知", value=0, disabled=False),
                ChoiceItem(label="男", value=1, disabled=False),
                ChoiceItem(label="女", value=2, disabled=False)
            ],
            "is_active": [
                ChoiceItem(label="启用", value=True, disabled=False),
                ChoiceItem(label="禁用", value=False, disabled=False)
            ],
            "is_staff": [
                ChoiceItem(label="是", value=True, disabled=False),
                ChoiceItem(label="否", value=False, disabled=False)
            ]
        }
    )


# 获取搜索字段
@router.get("/user/search-fields", response_model=SearchFieldsResponse)
async def get_user_search_fields(
    current_user: UserInfo = Depends(get_current_active_user)
):
    """获取用户搜索字段"""
    fields = [
        FieldInfo(name="username", label="用户名", field_type="string", required=False, choices=None),
        FieldInfo(name="nickname", label="昵称", field_type="string", required=False, choices=None),
        FieldInfo(name="email", label="邮箱", field_type="string", required=False, choices=None),
        FieldInfo(name="phone", label="手机号", field_type="string", required=False, choices=None),
        FieldInfo(
            name="gender", 
            label="性别", 
            field_type="choice", 
            required=False,
            choices=[
                ChoiceItem(label="未知", value=0, disabled=False),
                ChoiceItem(label="男", value=1, disabled=False),
                ChoiceItem(label="女", value=2, disabled=False)
            ]
        ),
        FieldInfo(
            name="is_active", 
            label="状态", 
            field_type="choice", 
            required=False,
            choices=[
                ChoiceItem(label="启用", value=True, disabled=False),
                ChoiceItem(label="禁用", value=False, disabled=False)
            ]
        )
    ]
    
    return SearchFieldsResponse(
        code=1000,
        detail="success",
        data=fields
    )


# 获取表格列
@router.get("/user/search-columns", response_model=SearchColumnsResponse)
async def get_user_search_columns(
    current_user: UserInfo = Depends(get_current_active_user)
):
    """获取用户表格列"""
    columns = [
        ColumnInfo(prop="id", label="ID", width=80, sortable=True, searchable=False, fixed=None),
        ColumnInfo(prop="username", label="用户名", width=120, sortable=True, searchable=True, fixed=None),
        ColumnInfo(prop="nickname", label="昵称", width=120, searchable=True, sortable=False, fixed=None),
        ColumnInfo(prop="email", label="邮箱", width=180, searchable=True, sortable=False, fixed=None),
        ColumnInfo(prop="phone", label="手机号", width=120, searchable=True, sortable=False, fixed=None),
        ColumnInfo(prop="dept_name", label="部门", width=120, sortable=False, searchable=False, fixed=None),
        ColumnInfo(prop="is_active", label="状态", width=80, sortable=False, searchable=False, fixed=None),
        ColumnInfo(prop="last_login", label="最后登录", width=160, sortable=True, searchable=False, fixed=None),
        ColumnInfo(prop="created_at", label="创建时间", width=160, sortable=True, searchable=False, fixed=None),
    ]
    
    return SearchColumnsResponse(
        code=1000,
        detail="success",
        data=columns
    )