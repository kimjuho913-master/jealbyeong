# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
import time
import webbrowser

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, FloatPrompt, IntPrompt
from rich.rule import Rule
from rich.progress_bar import ProgressBar

import plotly.graph_objects as go
import plotly.io as pio

pio.renderers.default = "vscode"

import platform
import matplotlib.font_manager as fm

# (과목 데이터는 이전과 동일)
SUBJECT_CATEGORIES = {
    "국어": [
        "독서(비문학)",
        "화법과 작문",
        "언어와 매체",
        "현대시",
        "고전시가",
        "현대소설",
        "고전소설",
        "극",
    ],
    "수학": ["수학1", "수학2", "미적분", "확률과 통계", "기하"],
    "영어": ["영어 듣기", "영어 단어", "영어독해연습", "영어 문법"],
    "사회탐구": [
        "생활과 윤리",
        "윤리와 사상",
        "한국지리",
        "세계지리",
        "동아시아사",
        "세계사",
        "경제",
        "정치와 법",
        "사회문화",
    ],
    "과학탐구": [
        "물리학1",
        "화학1",
        "생명과학1",
        "지구과학1",
        "물리학2",
        "화학2",
        "생명과학2",
        "지구과학2",
    ],
}
SUBJECT_TO_CATEGORY_MAP = {
    subject: category
    for category, subjects in SUBJECT_CATEGORIES.items()
    for subject in subjects
}

console = Console()
DATA_FILE = "study_log.csv"
GOAL_FILE = "study_goals.csv"


# --- ## 1. 새로운 시간 표시 형식 변환 함수 추가 ## ---
def format_time_display(decimal_minutes):
    """소수점 형태의 분(minutes)을 'M분 S초' 문자열로 변환합니다."""
    if pd.isna(decimal_minutes) or decimal_minutes < 0:
        return "0분 0초"
    total_seconds = int(decimal_minutes * 60)
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes}분 {seconds}초"


# --- ## 추가 끝 ## ---


def setup_korean_font():
    os_name = platform.system()
    if os_name == "Windows":
        font_name = "Malgun Gothic"
    elif os_name == "Darwin":
        font_name = "AppleGothic"
    elif os_name == "Linux":
        if any("NanumGothic" in font.name for font in fm.fontManager.ttflist):
            font_name = "NanumGothic"
        else:
            console.print(
                "[yellow]한글 폰트(나눔고딕)가 없어 일부 글자가 깨질 수 있습니다.[/yellow]"
            )
            font_name = None
    if font_name:
        plt.rc("font", family=font_name)
    plt.rc("axes", unicode_minus=False)


def add_study_record():
    console.print(Rule("[bold cyan]학습 기록 추가[/bold cyan]"))
    date_input = Prompt.ask(
        "- 날짜 (YYYY-MM-DD, 비워두면 오늘)",
        default=datetime.now().strftime("%Y-%m-%d"),
    )
    category_list = list(SUBJECT_CATEGORIES.keys())
    table = Table(show_header=False, show_edge=False, box=None)
    table.add_row(
        *[f"[bold cyan]{i+1}.[/bold cyan] {cat}" for i, cat in enumerate(category_list)]
    )
    console.print(table)
    category_choice_num = IntPrompt.ask(
        "학습할 과목의 [bold]대분류[/bold] 번호를 선택하세요",
        choices=[str(i + 1) for i in range(len(category_list))],
        show_choices=False,
    )
    selected_category = category_list[category_choice_num - 1]
    subject_list = SUBJECT_CATEGORIES[selected_category]
    if len(subject_list) == 1:
        selected_subject = subject_list[0]
        console.print(f"=> [green]{selected_subject}[/green] 과목이 선택되었습니다.")
    else:
        table = Table(show_header=False, show_edge=False, box=None)
        row_subjects = []
        for i, sub in enumerate(subject_list):
            row_subjects.append(f"[bold green]{i+1}.[/bold green] {sub}")
            if len(row_subjects) == 4:
                table.add_row(*row_subjects)
                row_subjects = []
        if row_subjects:
            table.add_row(*row_subjects)
        console.print(table)
        subject_choice_num = IntPrompt.ask(
            "학습할 [bold]세부 과목[/bold]의 번호를 선택하세요",
            choices=[str(i + 1) for i in range(len(subject_list))],
            show_choices=False,
        )
        selected_subject = subject_list[subject_choice_num - 1]
    console.print("\n[bold]공부 시간 측정 방법을 선택하세요:[/bold]")
    time_choice = Prompt.ask(
        "[bold]1.[/bold] 타이머 시작, [bold]2.[/bold] 수동으로 시간 입력",
        choices=["1", "2"],
        default="1",
    )
    if time_choice == "1":
        console.input(
            "\n[bold green] 타이머를 시작하려면 Enter 키를 누르세요... [/bold green]"
        )
        start_time = time.time()
        console.print(
            f"[cyan]{datetime.now().strftime('%H:%M:%S')}[/cyan] [bold]공부 시작![/bold] 💪"
        )
        console.input(
            "\n[bold red] 공부를 마치면 Enter 키를 눌러 타이머를 종료하세요... [/bold red]"
        )
        end_time = time.time()
        console.print(
            f"[cyan]{datetime.now().strftime('%H:%M:%S')}[/cyan] [bold]공부 종료![/bold] 🎉"
        )
        elapsed_seconds = end_time - start_time
        study_time_minutes = elapsed_seconds / 60
        # --- ## 2. 타이머 결과 표시 변경 ## ---
        time_display = format_time_display(study_time_minutes)
        console.print(
            f"\n총 공부 시간: [bold yellow]{time_display}[/bold yellow] ({study_time_minutes:.2f}분으로 저장됩니다)"
        )
        study_time = study_time_minutes
    else:
        study_time = FloatPrompt.ask("- 공부 시간 (분 단위)")
    content = Prompt.ask("- 구체적인 공부 내용")
    concentration = IntPrompt.ask(
        "- 집중도 (1~5)", choices=["1", "2", "3", "4", "5"], show_choices=False
    )
    new_record = {
        "날짜": [date_input],
        "과목": [selected_subject],
        "공부 시간(분)": [study_time],
        "공부 내용": [content],
        "집중도": [concentration],
    }
    df_new = pd.DataFrame(new_record)
    if not os.path.exists(DATA_FILE):
        df_new.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
        console.print(
            "[bold green]✅ 새 데이터 파일을 생성하고 기록을 저장했습니다.[/bold green]"
        )
    else:
        df_new.to_csv(
            DATA_FILE, mode="a", header=False, index=False, encoding="utf-8-sig"
        )
        console.print(
            "[bold green]✅ 기존 파일에 학습 기록을 추가했습니다.[/bold green]"
        )


def load_data():
    if not os.path.exists(DATA_FILE):
        return None
    df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
    df["날짜"] = pd.to_datetime(df["날짜"])
    return df


def show_visualizations():
    df = load_data()
    if df is None or df.empty:
        console.print("[yellow]분석할 데이터가 충분하지 않습니다.[/yellow]")
        return
    console.print(Rule("[bold cyan]통계 시각화[/bold cyan]"))
    console.print("1. 과목별 공부 시간 (대화형 원형 그래프)")
    console.print("2. 날짜별 총 공부 시간 및 집중도 변화 (막대+선 그래프)")
    choice = Prompt.ask(
        "보고 싶은 시각화 자료를 선택하세요", choices=["1", "2"], default="1"
    )
    if choice == "1":
        df["대분류"] = df["과목"].map(SUBJECT_TO_CATEGORY_MAP)
        df.dropna(subset=["대분류"], inplace=True)
        if df.empty:
            console.print("[yellow]분석할 데이터가 없습니다.[/yellow]")
            return

        # --- ## 4. 그래프 정보(Hover) 표시 변경 ## ---
        df_leaves = (
            df.groupby(["대분류", "과목"])
            .agg(
                total_time=("공부 시간(분)", "sum"),
                contents=("공부 내용", lambda x: "<br>- ".join(x.dropna().unique())),
            )
            .reset_index()
        )
        df_parents_agg = (
            df.groupby("대분류")
            .agg(
                total_time=("공부 시간(분)", "sum"),
                subject_list=("과목", lambda x: "<br>- ".join(sorted(x.unique()))),
            )
            .reset_index()
        )

        ids, labels, parents, values, hovertexts = [], [], [], [], []

        for index, row in df_parents_agg.iterrows():
            ids.append(row["대분류"])
            labels.append(row["대분류"])
            parents.append("")
            values.append(row["total_time"])
            time_display = format_time_display(row["total_time"])
            hovertexts.append(
                f"<b>{row['대분류']}</b><br><br><b>총 공부 시간:</b> {time_display}<br><br><b>기록된 세부 과목:</b><br>- {row['subject_list']}"
            )

        for index, row in df_leaves.iterrows():
            ids.append(f"{row['대분류']}-{row['과목']}")
            labels.append(row["과목"])
            parents.append(row["대분류"])
            values.append(row["total_time"])
            time_display = format_time_display(row["total_time"])
            hovertexts.append(
                f"<b>{row['과목']}</b><br><br><b>총 공부 시간:</b> {time_display}<br><br><b>공부 내용:</b><br>- {row['contents']}"
            )

        fig = go.Figure(
            go.Sunburst(
                ids=ids,
                labels=labels,
                parents=parents,
                values=values,
                branchvalues="total",
                insidetextorientation="radial",
                hovertext=hovertexts,
                hoverinfo="text",
            )
        )
        fig.update_layout(
            margin=dict(t=40, l=20, r=20, b=20),
            title_text="과목별 공부 시간 분포 (클릭하여 세부 항목 보기)",
            title_x=0.5,
        )
        chart_filename = "study_chart.html"
        fig.write_html(chart_filename, include_plotlyjs="inline")
        try:
            webbrowser.open_new_tab(chart_filename)
            console.print(
                f"\n[green]'{chart_filename}' 이름으로 그래프를 저장하고, 웹 브라우저에 표시했습니다.[/green]"
            )
        except webbrowser.Error:
            console.print(
                f"\n[yellow]웹 브라우저를 자동으로 여는 데 실패했습니다. '{chart_filename}' 파일을 직접 열어 확인해주세요.[/yellow]"
            )

    elif choice == "2":
        daily_stats = (
            df.groupby("날짜")
            .agg(
                total_time=("공부 시간(분)", "sum"),
                avg_concentration=("집중도", "mean"),
            )
            .sort_index()
        )
        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax1.bar(
            daily_stats.index,
            daily_stats["total_time"],
            color="skyblue",
            label="총 공부 시간(분)",
        )
        ax1.set_xlabel("날짜")
        ax1.set_ylabel("총 공부 시간(분)", color="skyblue")
        ax1.tick_params(axis="y", labelcolor="skyblue")
        ax2 = ax1.twinx()
        ax2.plot(
            daily_stats.index,
            daily_stats["avg_concentration"],
            color="salmon",
            marker="o",
            linestyle="--",
            label="평균 집중도",
        )
        ax2.set_ylabel("평균 집중도", color="salmon")
        ax2.tick_params(axis="y", labelcolor="salmon")
        ax2.set_ylim(0, 6)
        plt.title("날짜별 총 공부 시간 및 평균 집중도 변화 추이", fontsize=16)
        fig.tight_layout()
        plt.show()


def generate_feedback():
    df = load_data()
    if df is None or len(df) < 3:
        console.print(
            Panel(
                "[yellow]피드백을 생성하기에 데이터가 부족합니다.\n최소 3개 이상의 기록을 추가해주세요.[/yellow]",
                title="[bold]학습 피드백[/bold]",
                border_style="yellow",
            )
        )
        return
    console.print(Rule("[bold cyan]학습 피드백 시스템[/bold cyan]"))
    table = Table(
        title="[bold]나의 학습 습관 분석 결과[/bold]",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("분석 항목", style="cyan", width=20)
    table.add_column("결과 및 조언")
    avg_concentration_by_subject = df.groupby("과목")["집중도"].mean().sort_values()
    if (
        not avg_concentration_by_subject.empty
        and avg_concentration_by_subject.iloc[0] < 3
    ):
        lowest_conc_subj = avg_concentration_by_subject.index[0]
        lowest_conc_val = avg_concentration_by_subject.iloc[0]
        table.add_row(
            "⚠️ 집중도 취약 과목",
            f"과목 '[bold yellow]{lowest_conc_subj}[/bold yellow]'의 평균 집중도({lowest_conc_val:.1f})가 낮습니다.\n[italic]→ 기초 개념을 복습하거나, 학습 환경을 바꿔보세요.[/italic]",
        )
    total_study_time = df["공부 시간(분)"].sum()
    if total_study_time > 0:
        subject_proportion = (
            df.groupby("과목")["공부 시간(분)"].sum() / total_study_time
        ) * 100
        imbalanced_subjects = subject_proportion[subject_proportion < 10]
        if not imbalanced_subjects.empty:
            subjects_str = ", ".join(
                [f"'[bold yellow]{s}[/bold yellow]'" for s in imbalanced_subjects.index]
            )
            table.add_row(
                "📊 과목 불균형",
                f"과목 {subjects_str}의 학습 비중이 전체의 10% 미만입니다.\n[italic]→ 장기적인 성장을 위해 균형 있는 학습 계획이 필요합니다.[/italic]",
            )
    df["효율성 점수"] = df["집중도"] * df["공부 시간(분)"]
    efficiency_by_subject = (
        df.groupby("과목")["효율성 점수"].mean().sort_values(ascending=False)
    )
    if not efficiency_by_subject.empty:
        most_efficient_subject = efficiency_by_subject.index[0]
        table.add_row(
            "💡 최고 효율 과목",
            f"과목 '[bold green]{most_efficient_subject}[/bold green]'를 공부할 때 가장 높은 효율을 보입니다.\n[italic]→ 이 과목을 공부할 때의 성공 요인(시간, 장소, 방법 등)을 다른 과목에도 적용해보세요.[/italic]",
        )
    if table.row_count == 0:
        console.print(
            Panel(
                "[green]축하합니다! 현재 매우 균형 잡힌 학습을 하고 있습니다. 계속 유지해주세요![/green]",
                title="[bold]종합 분석[/bold]",
                border_style="green",
            )
        )
    else:
        console.print(table)


def set_weekly_goal():
    console.print(Rule("[bold cyan]주간 목표 설정[/bold cyan]"))
    goal_hours = FloatPrompt.ask("- 이번 주 목표 공부 시간을 입력하세요 (시간 단위)")
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    new_goal = {
        "주 시작일": [start_of_week.strftime("%Y-%m-%d")],
        "목표 시간(시간)": [goal_hours],
    }
    df_new_goal = pd.DataFrame(new_goal)
    if not os.path.exists(GOAL_FILE):
        df_new_goal.to_csv(GOAL_FILE, index=False, encoding="utf-8-sig")
    else:
        df_goals = pd.read_csv(GOAL_FILE, encoding="utf-8-sig")
        df_goals = df_goals[df_goals["주 시작일"] != start_of_week.strftime("%Y-%m-%d")]
        df_goals = pd.concat([df_goals, df_new_goal], ignore_index=True)
        df_goals.to_csv(GOAL_FILE, index=False, encoding="utf-8-sig")
    console.print(
        f"[bold green]✅ 이번 주 목표({goal_hours}시간)가 설정되었습니다.[/bold green]"
    )


def check_goal_achievement():
    console.print(Rule("[bold cyan]주간 목표 달성률 확인[/bold cyan]"))
    df_study = load_data()
    if not os.path.exists(GOAL_FILE):
        console.print(
            "[yellow]설정된 목표가 없습니다. 먼저 주간 목표를 설정해주세요.[/yellow]"
        )
        return
    df_goals = pd.read_csv(GOAL_FILE, encoding="utf-8-sig")
    df_goals["주 시작일"] = pd.to_datetime(df_goals["주 시작일"])
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    current_goal = df_goals[df_goals["주 시작일"].dt.date == start_of_week.date()]
    if current_goal.empty:
        console.print("[yellow]이번 주 목표가 설정되지 않았습니다.[/yellow]")
        return
    goal_hours = current_goal["목표 시간(시간)"].iloc[0]
    study_minutes_this_week = 0
    if df_study is not None:
        this_week_data = df_study[df_study["날짜"] >= start_of_week]
        study_minutes_this_week = this_week_data["공부 시간(분)"].sum()
    study_hours_this_week = study_minutes_this_week / 60
    achievement_rate = (
        (study_hours_this_week / goal_hours) * 100 if goal_hours > 0 else 0
    )
    table = Table(show_header=False, box=None, padding=0)
    table.add_column(width=20)
    table.add_column()
    table.add_row("🎯 이번 주 목표", f"[bold cyan]{goal_hours:.1f}[/bold cyan] 시간")
    table.add_row(
        "📖 현재 공부 시간",
        f"[bold green]{study_hours_this_week:.1f}[/bold green] 시간",
    )
    console.print(table)
    console.print("\n[bold]🏆 달성률: {:.2f} %[/bold]".format(achievement_rate))
    progress = ProgressBar(total=100, completed=min(achievement_rate, 100), width=50)
    console.print(progress)


def delete_study_record():
    console.print(Rule("[bold red]학습 기록 삭제[/bold red]"))
    df = load_data()
    if df is None or df.empty:
        console.print("[yellow]삭제할 기록이 없습니다.[/yellow]")
        return
    table = Table(title="전체 학습 기록", show_header=True, header_style="bold magenta")
    table.add_column("번호", style="dim", width=6)
    table.add_column("날짜", style="cyan")
    table.add_column("과목", style="green")
    table.add_column("공부 시간", justify="right")
    table.add_column("집중도", justify="right")

    for index, row in df.iterrows():
        # --- ## 3. 삭제 목록 표시 변경 ## ---
        time_display = format_time_display(row["공부 시간(분)"])
        table.add_row(
            str(index),
            row["날짜"].strftime("%Y-%m-%d"),
            row["과목"],
            time_display,
            str(row["집중도"]),
        )

    console.print(table)
    console.print("[yellow]삭제를 원하지 않으면 'c'를 입력하세요.[/yellow]")
    while True:
        try:
            choice = Prompt.ask("삭제할 기록의 '번호'를 입력하세요")
            if choice.lower() == "c":
                console.print("[green]삭제를 취소했습니다.[/green]")
                return
            record_to_delete = int(choice)
            if record_to_delete in df.index:
                break
            else:
                console.print(
                    "[red]오류: 목록에 없는 번호입니다. 다시 입력해주세요.[/red]"
                )
        except ValueError:
            console.print("[red]오류: 숫자 또는 'c'만 입력해주세요.[/red]")
    confirm = Prompt.ask(
        f"정말로 [bold red]'{df.loc[record_to_delete, '과목']}'[/bold red] 기록을 삭제하시겠습니까?",
        choices=["y", "n"],
        default="n",
    )
    if confirm.lower() == "y":
        df.drop(record_to_delete, inplace=True)
        df.reset_index(drop=True, inplace=True)
        df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
        console.print("[bold green]✅ 기록이 성공적으로 삭제되었습니다.[/bold green]")
    else:
        console.print("[green]삭제를 취소했습니다.[/green]")


def main():
    setup_korean_font()
    while True:
        console.print(
            Panel(
                "[bold]1.[/bold] 공부 기록 추가\n[bold]2.[/bold] 통계 및 시각화 보기\n[bold]3.[/bold] 학습 피드백 받기\n[bold]4.[/bold] 주간 목표 설정\n[bold]5.[/bold] 주간 목표 달성률 확인\n[bold red]6.[/bold red] 학습 기록 삭제\n[bold]7.[/bold] 프로그램 종료",
                title="📊 [bold green]학습 관리 및 분석 프로그램[/bold green] 📊",
                subtitle="원하는 기능의 번호를 입력하세요",
                border_style="blue",
            )
        )
        choice = Prompt.ask("선택", choices=["1", "2", "3", "4", "5", "6", "7"])
        if choice == "1":
            add_study_record()
        elif choice == "2":
            show_visualizations()
        elif choice == "3":
            generate_feedback()
        elif choice == "4":
            set_weekly_goal()
        elif choice == "5":
            check_goal_achievement()
        elif choice == "6":
            delete_study_record()
        elif choice == "7":
            console.print(
                "[bold magenta]프로그램을 종료합니다. 꾸준한 학습을 응원합니다! 💪[/bold magenta]"
            )
            break


if __name__ == "__main__":
    main()
