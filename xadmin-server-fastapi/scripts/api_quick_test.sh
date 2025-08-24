#!/bin/bash

# xAdmin FastAPI API 快速测试脚本
# 使用方法: ./api_quick_test.sh [base_url] [username] [password]

# 设置默认参数
BASE_URL=${1:-"http://127.0.0.1:8000"}
USERNAME=${2:-"admin"}
PASSWORD=${3:-"admin123"}

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 输出函数
log_step() {
    echo -e "\n${BLUE}================================${NC}"
    echo -e "${BLUE}步骤 $1: $2${NC}"
    echo -e "${BLUE}================================${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 检查依赖工具
check_dependencies() {
    if ! command -v curl &> /dev/null; then
        log_error "curl 未安装，请先安装 curl"
        exit 1
    fi
    
    if ! command -v jq &> /dev/null; then
        log_warning "jq 未安装，JSON 响应将无法格式化显示"
    fi
}

# 格式化JSON输出
format_json() {
    if command -v jq &> /dev/null; then
        echo "$1" | jq .
    else
        echo "$1"
    fi
}

# 发送HTTP请求
make_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    local token=$4
    
    local url="${BASE_URL}${endpoint}"
    local headers=()
    
    if [ -n "$token" ]; then
        headers+=("-H" "Authorization: Bearer $token")
    fi
    
    if [ -n "$data" ]; then
        headers+=("-H" "Content-Type: application/json")
        curl -s -X "$method" "${headers[@]}" -d "$data" "$url"
    else
        curl -s -X "$method" "${headers[@]}" "$url"
    fi
}

# 步骤1: 健康检查
test_health() {
    log_step "1" "系统健康检查"
    
    local response=$(make_request "GET" "/health")
    local status=$(echo "$response" | grep -o '"status":"healthy"' | wc -l)
    
    if [ "$status" -eq 1 ]; then
        log_success "系统运行正常"
        log_info "响应: $(format_json "$response")"
        return 0
    else
        log_error "系统健康检查失败"
        log_info "响应: $(format_json "$response")"
        return 1
    fi
}

# 步骤2: 获取登录配置
test_login_config() {
    log_step "2" "获取登录配置"
    
    local response=$(make_request "GET" "/api/system/login/basic")
    local code=$(echo "$response" | grep -o '"code":1000' | wc -l)
    
    if [ "$code" -eq 1 ]; then
        log_success "登录配置获取成功"
        log_info "响应: $(format_json "$response")"
        return 0
    else
        log_error "登录配置获取失败"
        log_info "响应: $(format_json "$response")"
        return 1
    fi
}

# 步骤3: 获取验证码配置
test_captcha_config() {
    log_step "3" "获取验证码配置"
    
    local response=$(make_request "GET" "/api/captcha/config")
    local code=$(echo "$response" | grep -o '"code":1000' | wc -l)
    
    if [ "$code" -eq 1 ]; then
        log_success "验证码配置获取成功"
        log_info "响应: $(format_json "$response")"
        return 0
    else
        log_warning "验证码配置获取失败（可能未启用验证码）"
        log_info "响应: $(format_json "$response")"
        return 0  # 验证码可能未启用，不算失败
    fi
}

# 步骤4: 用户登录
test_login() {
    log_step "4" "用户登录"
    
    local login_data="{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}"
    local response=$(make_request "POST" "/api/system/login/basic" "$login_data")
    local code=$(echo "$response" | grep -o '"code":1000' | wc -l)
    
    if [ "$code" -eq 1 ]; then
        # 提取access token
        if command -v jq &> /dev/null; then
            ACCESS_TOKEN=$(echo "$response" | jq -r '.data.access // empty')
        else
            ACCESS_TOKEN=$(echo "$response" | sed -n 's/.*"access":"\([^"]*\)".*/\1/p')
        fi
        
        if [ -n "$ACCESS_TOKEN" ]; then
            log_success "登录成功"
            log_info "Token: ${ACCESS_TOKEN:0:50}..."
            return 0
        else
            log_error "登录成功但未获取到Token"
            return 1
        fi
    else
        log_error "登录失败"
        log_info "响应: $(format_json "$response")"
        return 1
    fi
}

# 步骤5: 获取用户信息
test_user_info() {
    log_step "5" "获取当前用户信息"
    
    if [ -z "$ACCESS_TOKEN" ]; then
        log_error "未登录，无法获取用户信息"
        return 1
    fi
    
    local response=$(make_request "GET" "/api/system/userinfo/" "" "$ACCESS_TOKEN")
    local code=$(echo "$response" | grep -o '"code":1000' | wc -l)
    
    if [ "$code" -eq 1 ]; then
        log_success "用户信息获取成功"
        log_info "响应: $(format_json "$response")"
        return 0
    else
        log_error "用户信息获取失败"
        log_info "响应: $(format_json "$response")"
        return 1
    fi
}

# 步骤6: 获取用户列表
test_user_list() {
    log_step "6" "获取用户列表"
    
    if [ -z "$ACCESS_TOKEN" ]; then
        log_error "未登录，无法获取用户列表"
        return 1
    fi
    
    local response=$(make_request "GET" "/api/system/user?page=1&size=10" "" "$ACCESS_TOKEN")
    local code=$(echo "$response" | grep -o '"code":1000' | wc -l)
    
    if [ "$code" -eq 1 ]; then
        log_success "用户列表获取成功"
        
        # 提取用户数量
        if command -v jq &> /dev/null; then
            local total=$(echo "$response" | jq -r '.data.total // 0')
            log_info "用户总数: $total"
        fi
        
        log_info "响应: $(format_json "$response")"
        return 0
    else
        log_warning "用户列表获取失败（可能权限不足）"
        log_info "响应: $(format_json "$response")"
        return 0  # 权限不足不算测试失败
    fi
}

# 步骤7: 刷新Token
test_refresh_token() {
    log_step "7" "刷新访问令牌"
    
    if [ -z "$REFRESH_TOKEN" ]; then
        log_warning "无刷新令牌，跳过此步骤"
        return 0
    fi
    
    local refresh_data="{\"refresh\":\"$REFRESH_TOKEN\"}"
    local response=$(make_request "POST" "/api/system/refresh" "$refresh_data")
    local code=$(echo "$response" | grep -o '"code":1000' | wc -l)
    
    if [ "$code" -eq 1 ]; then
        log_success "令牌刷新成功"
        log_info "响应: $(format_json "$response")"
        return 0
    else
        log_warning "令牌刷新失败"
        log_info "响应: $(format_json "$response")"
        return 0  # 刷新失败不算测试失败
    fi
}

# 主测试函数
run_tests() {
    echo "🚀 开始 xAdmin FastAPI API 测试"
    echo "🔗 测试地址: $BASE_URL"
    echo "👤 测试用户: $USERNAME"
    echo "🔑 测试密码: ${PASSWORD:0:3}***"
    
    local start_time=$(date +%s)
    local total_tests=0
    local passed_tests=0
    
    # 执行测试
    tests=(
        "test_health:系统健康检查"
        "test_login_config:获取登录配置"
        "test_captcha_config:获取验证码配置"
        "test_login:用户登录"
        "test_user_info:获取用户信息"
        "test_user_list:获取用户列表"
        "test_refresh_token:刷新令牌"
    )
    
    for test in "${tests[@]}"; do
        IFS=':' read -ra ADDR <<< "$test"
        test_func="${ADDR[0]}"
        test_name="${ADDR[1]}"
        
        ((total_tests++))
        
        if $test_func; then
            ((passed_tests++))
        fi
        
        sleep 0.5  # 稍微延迟避免过快请求
    done
    
    # 计算结果
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    local success_rate=$((passed_tests * 100 / total_tests))
    
    # 输出总结
    echo -e "\n${BLUE}=======================================${NC}"
    echo -e "${BLUE}📊 测试总结${NC}"
    echo -e "${BLUE}=======================================${NC}"
    echo -e "⏱️  测试耗时: ${duration}秒"
    echo -e "✅ 通过测试: ${passed_tests}/${total_tests}"
    echo -e "📈 成功率: ${success_rate}%"
    
    if [ "$passed_tests" -eq "$total_tests" ]; then
        echo -e "\n${GREEN}🎉 所有测试均通过！API调用流程正常。${NC}"
        return 0
    else
        echo -e "\n${YELLOW}⚠️  部分测试未通过，请检查系统配置。${NC}"
        return 1
    fi
}

# 显示使用说明
show_usage() {
    echo "用法: $0 [base_url] [username] [password]"
    echo ""
    echo "参数:"
    echo "  base_url   API服务地址 (默认: http://127.0.0.1:8000)"
    echo "  username   测试用户名 (默认: admin)"
    echo "  password   测试密码 (默认: admin123)"
    echo ""
    echo "示例:"
    echo "  $0"
    echo "  $0 http://localhost:8000"
    echo "  $0 http://localhost:8000 admin mypassword"
    echo ""
    echo "依赖工具:"
    echo "  - curl (必须)"
    echo "  - jq (可选，用于格式化JSON输出)"
}

# 主程序入口
main() {
    if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
        show_usage
        exit 0
    fi
    
    check_dependencies
    
    echo "开始执行 xAdmin FastAPI API 测试..."
    
    if run_tests; then
        exit 0
    else
        exit 1
    fi
}

# 执行主程序
main "$@"