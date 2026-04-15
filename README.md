# 医保限制解除工具 - 使用说明

## 环境要求

1. **Python 3.6+** 已安装
2. **Oracle Client** 已安装并配置
3. **cx_Oracle** Python库已安装

## 安装依赖

### 1. 安装 cx_Oracle

打开命令提示符（cmd），运行：

```bash
pip install cx_Oracle
```

### 2. 安装 Oracle Instant Client

- 从 Oracle 官网下载 Oracle Instant Client
- 解压到某个目录，例如：`C:\oracle\instantclient_19_8`
- 将该目录添加到系统环境变量 PATH 中

## 配置数据库连接

编辑 `oracle_db_tool.py` 文件，修改第 7-11 行的数据库配置：

```python
DB_CONFIG = {
    'user': 'your_username',      # 改为你的数据库用户名
    'password': 'your_password',  # 改为你的数据库密码
    'dsn': 'your_host:your_port/your_service_name'  # 改为你的数据库连接信息
}
```

示例：
```python
DB_CONFIG = {
    'user': 'scott',
    'password': 'tiger',
    'dsn': '192.168.1.100:1521/orcl'
}
```

## 运行程序

### 方法一：双击运行

直接双击 `oracle_db_tool.py` 文件即可运行（需要确保 .py 文件关联了 Python）

### 方法二：命令行运行

1. 打开命令提示符（cmd）
2. 切换到程序所在目录：
   ```bash
   cd d:\work\Medical_insurance_lifting_restrictions
   ```
3. 运行程序：
   ```bash
   python oracle_db_tool.py
   ```

## 使用方法

1. **输入 Patient ID**：在输入框中输入患者ID，格式如：T001814223
2. **点击"搜索处方"**：或直接按回车键
3. **查看结果**：程序会显示最新的10条处方记录（按就诊日期降序排列）
4. **选择处方**：点击表格中的某一行来选择要取消限制的处方
5. **点击"取消限制"**：会弹出确认对话框
6. **确认操作**：点击"是"确认取消限制，程序会：
   - 更新选中处方的 drug_days 为 1
   - 查询对应的 doctor_no
   - 将 APP_CONFIGER_PARAMETER 表中 YB_YBSHARE 参数值改为 0

## 注意事项

1. **数据安全**：请谨慎操作，确保输入正确的 Patient ID
2. **数据库权限**：确保数据库用户有相应的查询和更新权限
3. **备份数据**：建议在执行更新操作前备份相关数据
4. **网络连接**：确保能够正常连接到 Oracle 数据库服务器

## 常见问题

### 1. 无法连接数据库
- 检查数据库配置是否正确
- 确认网络连接正常
- 验证 Oracle Client 是否正确安装

### 2. 找不到 cx_Oracle 模块
- 运行 `pip install cx_Oracle` 安装
- 确认使用的是正确的 Python 版本

### 3. OCI.dll 加载失败
- 确认 Oracle Instant Client 已正确安装
- 检查环境变量 PATH 是否包含 Instant Client 目录
- 确保 Instant Client 版本与 Python 版本匹配（32位/64位）

## 技术支持

如有问题，请联系系统管理员或开发团队。
