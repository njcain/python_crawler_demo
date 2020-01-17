# 遍历当前文件夹下的所有excel文件，提取其中的手机号码并过滤出上海的手机号存储到新的excel中

import os
import xlrd
import xlsxwriter
import sys
import re
import io
from phone import Phone

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
# os.walk()遍历文件夹下的所有文件
# os.walk()获得三组数据(rootdir, dirname,filnames)
type = sys.getfilesystemencoding()
failed_file_paths = []
p = Phone()
def file_path(file_dir):
    source_xls=[]
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            tmp_path = "%s/%s" % (root,file)
            if os.path.splitext(file)[1] == '.xls':
                source_xls.append(tmp_path)
            elif os.path.splitext(file)[1] == '.xlsx':
                source_xls.append(tmp_path)
            else:
                failed_file_paths.append(tmp_path)
    return source_xls


source_xls=file_path("./")
#if len(sys.argv) != 2:
#    print("请输入一个要合成的文件名，文件名推荐以xls结尾，此程序不可重复使用，重复使用需删除已合成的文件")
#    exit()
#else:
target_xls = "wh.xlsx"

#print("totally merged these files:")
#print(source_xls)
#print()

# 读取数据
data=[]

exceps=[]
for i in source_xls:
    print()
    print(i)
    try:
        wb = xlrd.open_workbook(i)
        for sheet in wb.sheets():
            for rownum in range(sheet.nrows):
                tmp_datas=sheet.row_values(rownum)
                tmp_datas_true=[]
                for tmp_data in tmp_datas:
                    cell_nums=re.findall(r'1\d{10}', str(tmp_data))
                    if cell_nums:
                        for cell_num in cell_nums:
                            if p.find(cell_num)['province'] == '上海':
                                tmp_datas_true.append(cell_num)
                if tmp_datas_true:
                    for tmp_data_true in tmp_datas_true:
                        data.append(tmp_data_true)
                        print(tmp_data_true)
    except Exception as e:
        exceps.append(e)
        failed_file_paths.append(i)

print()

# 写入数据
workbook = xlsxwriter.Workbook(target_xls)
worksheet = workbook.add_worksheet()
worksheet.set_column('A:A', 20)
font=workbook.add_format({'num_format': '@','bold': True,"font_size": 14})
data_filtered=list(set(data))
#data_filtered.sort(key=data.index)
for i in range(len(data_filtered)):
#    for j in range(len(data[i])):
    worksheet.write(i, 0, data_filtered[i], font) # i表示行，0表示列
# 关闭文件流
workbook.close()

failed_file_paths_txt="failed_file_paths.txt"
with open(failed_file_paths_txt,'w',encoding="utf-8") as file_object:
    file_object.write("已下文件由于各种原因需要手动合并:\n")
    for failed_file_path in failed_file_paths:
        file_object.write("%s\n" % (failed_file_path,))
#for excep in exceps:
#    print(excep)

print("note: 有些文件需要手动合并，请到 failed_file_paths.txt 里面查看")
