mcno = "211"
dst = "20240213"
shift= "1"

curly ="{{}}"
print
date_url = f"\"date\":\"{dst}\",\"shift\":\"{shift}\""
print({date_url})

formatted = f"{{\"mcno\":\"{mcno}\",\"date\":{{{date_url}}}}}"
print(formatted)