import oracledb
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import logging
from datetime import datetime

# 配置日志
log_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(log_dir, 'operation.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()  # 同时输出到控制台
    ]
)
logger = logging.getLogger(__name__)

# 尝试初始化 Thick 模式（需要 Oracle Instant Client）
try:
    # 可以指定 Oracle Instant Client 的路径，如果已添加到 PATH 则不需要
    # oracledb.init_oracle_client(lib_dir=r"C:\oracle\instantclient_19_8")
    oracledb.init_oracle_client()
    print("Oracle Thick mode initialized successfully")
except Exception as e:
    print(f"Warning: Could not initialize Thick mode: {e}")
    print("Will try to use Thin mode (may not work with older Oracle versions)")

# 数据库配置信息（请根据实际情况修改）
DB_CONFIG = {
    'user': '你的数据库用户名',      # 数据库用户名
    'password': '你的数据库密码',  # 数据库密码
    'dsn': 'localhost:1521/orcl'  # 数据库连接字符串，例如：localhost:1521/orcl
}

class OracleDBApp:
    def __init__(self, root):
        self.root = root
        self.root.title("医保限制解除工具")
        self.root.geometry("800x600")
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Patient ID 输入框
        ttk.Label(main_frame, text="Patient ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.patient_id_var = tk.StringVar()
        patient_entry = ttk.Entry(main_frame, textvariable=self.patient_id_var, width=30)
        patient_entry.grid(row=0, column=1, pady=5, padx=5)
        patient_entry.bind('<Return>', lambda e: self.search_prescriptions())
        
        # 搜索按钮
        search_btn = ttk.Button(main_frame, text="搜索处方", command=self.search_prescriptions)
        search_btn.grid(row=0, column=2, pady=5, padx=5)
        
        # 患者姓名显示
        ttk.Label(main_frame, text="患者姓名:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.patient_name_var = tk.StringVar(value="")
        name_label = ttk.Label(main_frame, textvariable=self.patient_name_var, foreground="blue", font=("Arial", 10, "bold"))
        name_label.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        # 结果表格
        columns = ('visit_date', 'drug_name')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=10)
        
        # 定义列标题
        self.tree.heading('visit_date', text='就诊日期')
        self.tree.heading('drug_name', text='药品名称')
        
        # 设置列宽
        self.tree.column('visit_date', width=150)
        self.tree.column('drug_name', width=400)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        scrollbar.grid(row=2, column=3, sticky=(tk.N, tk.S))
        
        # 取消限制按钮
        cancel_btn = ttk.Button(main_frame, text="取消限制", command=self.cancel_restriction)
        cancel_btn.grid(row=3, column=1, pady=10)
        
        # 状态标签
        self.status_var = tk.StringVar(value="请输入Patient ID并点击搜索")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=4, column=0, columnspan=3, pady=5)
        
        # 存储当前选中的数据
        self.current_data = []
        
    def get_db_connection(self):
        """获取数据库连接"""
        try:
            # 使用 Thin 模式连接（不需要 Oracle Instant Client）
            connection = oracledb.connect(
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                dsn=DB_CONFIG['dsn']
            )
            return connection
        except oracledb.Error as error:
            messagebox.showerror("数据库错误", f"连接数据库失败: {error}")
            return None
    
    def get_patient_name(self, patient_id):
        """获取患者姓名"""
        connection = self.get_db_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor()
            sql = "SELECT name FROM pat_master_index WHERE patient_id = :patient_id"
            cursor.execute(sql, {'patient_id': patient_id})
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return result[0]
            else:
                return None
        except oracledb.Error as error:
            logger.error(f"查询患者姓名失败: {error}")
            return None
        finally:
            connection.close()
    
    def search_prescriptions(self):
        """搜索处方记录"""
        patient_id = self.patient_id_var.get().strip()
        
        if not patient_id:
            messagebox.showwarning("警告", "请输入Patient ID")
            return
        
        # 记录查询操作
        logger.info(f"查询操作 - Patient ID: {patient_id}")
        
        # 查询患者姓名
        patient_name = self.get_patient_name(patient_id)
        if patient_name:
            self.patient_name_var.set(patient_name)
            logger.info(f"患者姓名: {patient_name}")
        else:
            self.patient_name_var.set("未找到")
            logger.warning(f"未找到Patient ID {patient_id} 对应的患者姓名")
        
        self.status_var.set("正在查询...")
        self.root.update()
        
        connection = self.get_db_connection()
        if not connection:
            return
        
        try:
            cursor = connection.cursor()
            
            # 执行查询SQL（使用ROWNUM兼容旧版Oracle）
            sql = """
                SELECT visit_date, visit_no, drug_name FROM (
                    SELECT a.visit_date, a.visit_no, a.drug_name 
                    FROM outp_presc a 
                    WHERE (a.visit_date, a.visit_no) IN (
                        SELECT visit_date, visit_no 
                        FROM outp_orders 
                        WHERE patient_id = :patient_id
                    )
                    ORDER BY a.visit_date DESC
                )
                WHERE ROWNUM <= 10
            """
            
            cursor.execute(sql, {'patient_id': patient_id})
            rows = cursor.fetchall()
            
            # 记录查询结果
            logger.info(f"查询结果 - 找到 {len(rows)} 条记录")
            for i, row in enumerate(rows, 1):
                visit_date, visit_no, drug_name = row
                if hasattr(visit_date, 'strftime'):
                    date_str = visit_date.strftime('%Y-%m-%d')
                else:
                    date_str = str(visit_date)
                logger.info(f"  记录{i}: visit_date={date_str}, visit_no={visit_no}, drug_name={drug_name}")
            
            # 清空现有数据
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # 存储数据并填充表格
            self.current_data = []
            for row in rows:
                visit_date, visit_no, drug_name = row
                # 格式化日期显示
                if hasattr(visit_date, 'strftime'):
                    date_str = visit_date.strftime('%Y-%m-%d')
                else:
                    date_str = str(visit_date)
                
                self.tree.insert('', tk.END, values=(date_str, drug_name))
                self.current_data.append({
                    'visit_date': visit_date,
                    'visit_no': visit_no,  # 保存 visit_no
                    'drug_name': drug_name
                })
            
            if len(rows) == 0:
                self.status_var.set(f"未找到Patient ID为 {patient_id} 的处方记录")
            else:
                self.status_var.set(f"找到 {len(rows)} 条记录，请选择要取消限制的处方")
            
            cursor.close()
            
        except oracledb.Error as error:
            logger.error(f"查询失败: {error}")
            messagebox.showerror("查询错误", f"查询失败: {error}")
            self.status_var.set("查询失败")
        finally:
            connection.close()
    
    def cancel_restriction(self):
        """取消限制"""
        # 获取选中的项目
        selected_items = self.tree.selection()
        
        if not selected_items:
            messagebox.showwarning("警告", "请先选择一条处方记录")
            return
        
        # 获取选中项的数据
        selected_item = selected_items[0]
        item_values = self.tree.item(selected_item, 'values')
        selected_visit_date_str = item_values[0]
        selected_drug_name = item_values[1]
        
        # 记录操作开始
        logger.info(f"=" * 60)
        logger.info(f"取消限制操作开始")
        logger.info(f"选中记录: visit_date={selected_visit_date_str}, drug_name={selected_drug_name}")
        
        # 找到对应的原始数据
        selected_data = None
        for data in self.current_data:
            if hasattr(data['visit_date'], 'strftime'):
                date_str = data['visit_date'].strftime('%Y-%m-%d')
            else:
                date_str = str(data['visit_date'])
            
            if date_str == selected_visit_date_str and data['drug_name'] == selected_drug_name:
                selected_data = data
                break
        
        if not selected_data:
            messagebox.showerror("错误", "无法获取选中记录的详细信息")
            return
        
        # 确认对话框
        confirm = messagebox.askyesno(
            "确认操作",
            f"确定要取消以下处方的限制吗？\n\n"
            f"就诊日期: {selected_visit_date_str}\n"
            f"药品名称: {selected_drug_name}"
        )
        
        if not confirm:
            logger.info("用户取消了操作")
            return
        
        self.status_var.set("正在处理...")
        self.root.update()
        
        connection = self.get_db_connection()
        if not connection:
            return
        
        try:
            cursor = connection.cursor()
            
            # 第一步：更新outp_presc表的drug_days为1
            logger.info(f"执行更新: outp_presc.drug_days = 1")
            logger.info(f"  条件: visit_date={selected_data['visit_date']}, visit_no={selected_data['visit_no']}")
            
            update_presc_sql = """
                UPDATE outp_presc 
                SET drug_days = 1 
                WHERE visit_date = :visit_date 
                AND visit_no = :visit_no
            """
            
            cursor.execute(update_presc_sql, {
                'visit_date': selected_data['visit_date'],
                'visit_no': selected_data['visit_no']
            })
            
            logger.info(f"  影响行数: {cursor.rowcount}")
            logger.info(f"  更新成功: drug_days 已设置为 1")
            
            # 第二步：从outp_orders获取doctor_no
            logger.info(f"查询: 从 outp_orders 获取 doctor_no")
            logger.info(f"  条件: visit_date={selected_data['visit_date']}, visit_no={selected_data['visit_no']}")
            
            get_doctor_sql = """
                SELECT doctor_no 
                FROM outp_orders 
                WHERE visit_date = :visit_date 
                AND visit_no = :visit_no
            """
            
            cursor.execute(get_doctor_sql, {
                'visit_date': selected_data['visit_date'],
                'visit_no': selected_data['visit_no']
            })
            
            doctor_result = cursor.fetchone()
            
            if not doctor_result:
                logger.warning(f"未找到对应的医生编号")
                messagebox.showwarning("警告", "未找到对应的医生编号")
                cursor.close()
                connection.rollback()
                self.status_var.set("操作失败：未找到医生编号")
                return
            
            doctor_no = doctor_result[0]
            logger.info(f"  查询结果: doctor_no = {doctor_no}")
            
            # 第三步：更新APP_CONFIGER_PARAMETER表
            logger.info(f"执行更新: APP_CONFIGER_PARAMETER.PARAMETER_VALUE = '0'")
            logger.info(f"  条件: PARAMETER_NAME = 'YB_YBSHARE'")
            
            update_config_sql = """
                UPDATE APP_CONFIGER_PARAMETER 
                SET PARAMETER_VALUE = '0' 
                WHERE PARAMETER_NAME = 'YB_YBSHARE'
            """
            
            cursor.execute(update_config_sql)
            logger.info(f"  影响行数: {cursor.rowcount}")
            logger.info(f"  更新成功: YB_YBSHARE 已设置为 0")
            
            # 提交事务
            connection.commit()
            
            logger.info(f"事务已提交")
            logger.info(f"取消限制操作完成")
            logger.info(f"=" * 60)
            
            messagebox.showinfo("成功", "限制已成功取消！")
            self.status_var.set("操作成功完成")
            
            cursor.close()
            
        except oracledb.Error as error:
            logger.error(f"更新失败: {error}")
            logger.error(f"操作回滚")
            connection.rollback()
            messagebox.showerror("更新错误", f"更新失败: {error}")
            self.status_var.set("操作失败")
        finally:
            connection.close()


def main():
    logger.info("="*60)
    logger.info("程序启动")
    logger.info(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"日志文件: {log_file}")
    logger.info("="*60)
    
    root = tk.Tk()
    app = OracleDBApp(root)
    
    # 窗口关闭时记录
    def on_closing():
        logger.info("程序退出")
        logger.info("="*60)
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
