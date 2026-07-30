from openpyxl import load_workbook
from best_buds_weight_station.spreadsheet import append_xlsx,append_csv,HEADERS

def test_formula_injection(tmp_path):
 r={h:'' for h in HEADERS}; r.update({'sequence':1,'record_id':'1','barcode_raw':'=HYPERLINK("x")'})
 append_xlsx(tmp_path/'a.xlsx',r); ws=load_workbook(tmp_path/'a.xlsx').active; assert str(ws.cell(2,4).value).startswith("'=")
 append_csv(tmp_path/'a.csv',r); assert "'=HYPERLINK" in (tmp_path/'a.csv').read_text()
def test_compatible_continuation(tmp_path):
 r={h:h for h in HEADERS}; append_xlsx(tmp_path/'a.xlsx',r); append_xlsx(tmp_path/'a.xlsx',r); assert load_workbook(tmp_path/'a.xlsx').active.max_row==3
