import plotly.graph_objects as go
import webbrowser

# 가장 단순한 막대 그래프를 만듭니다.
fig = go.Figure(go.Bar(x=['A', 'B', 'C'], y=[10, 20, 15]))

# 인터넷 연결 없이도 열리도록 HTML 파일로 저장합니다.
fig.write_html("test.html", include_plotlyjs='inline')

# 저장된 파일을 브라우저에서 엽니다.
webbrowser.open_new_tab("test.html")

print("'test.html' 파일을 생성하고 브라우저에서 열었습니다.")