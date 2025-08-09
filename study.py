import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, FloatPrompt, IntPrompt
from rich.rule import Rule
from rich.progress_bar import ProgressBar

import platform
import matplotlib.font_manager as fm

def setup_korean_font():
    os_name = platform.system()
    if os_name == 'Windows': font_name = 'Malgun Gothic'
    elif os_name == 'Darwin': font_name = 'AppleGothic'
    elif os_name == 'Linux':
        if any('NanumGothic' in font.name for font in fm.fontManager.ttflist):
            font_name = 'NanumGothic'
        else:
            console.print("[yellow]한글 폰트(나눔고딕)가 없어 일부 글자가 깨질 수 있습니다.[/yellow]")
            font_name = None
    if font_name:
        plt.rc('font', family=font_name)
    plt.rc('axes', unicode_minus=False)

DATA_FILE = 'study_log.csv'
GOAL_FILE = 'study_goals.csv'
console = Console()

def add_study_record():
    """사용자로부터 학습 데이터를 입력받아 CSV 파일에 저장합니다. (## UI 개선)"""
    console.print(Rule("[bold cyan]학습 기록 추가[/bold cyan]"))
    
    date_input = Prompt.ask("- 날짜 (YYYY-MM-DD, 비워두면 오늘)", default=datetime.now().strftime('%Y-%m-%d'))
    subject = Prompt.ask("- 과목명")
    study_time = FloatPrompt.ask("- 공부 시간 (분 단위)")
    content = Prompt.ask("- 구체적인 공부 내용")
    concentration = IntPrompt.ask("- 집중도 (1~5)", choices=['1','2','3','4','5'], show_choices=False)

    new_record = {
        '날짜': [date_input], '과목': [subject], '공부 시간(분)': [study_time],
        '공부 내용': [content], '집중도': [concentration]
    }
    df_new = pd.DataFrame(new_record)

    if not os.path.exists(DATA_FILE):
        df_new.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
        console.print("[bold green]✅ 새 데이터 파일을 생성하고 기록을 저장했습니다.[/bold green]")
    else:
        df_new.to_csv(DATA_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')
        console.print("[bold green]✅ 기존 파일에 학습 기록을 추가했습니다.[/bold green]")


def load_data():
    if not os.path.exists(DATA_FILE):
        console.print("[yellow]데이터 파일이 없습니다. 먼저 학습 기록을 추가해주세요.[/yellow]")
        return None
    df = pd.read_csv(DATA_FILE, encoding='utf-8-sig')
    df['날짜'] = pd.to_datetime(df['날짜'])
    return df


def show_visualizations():
    df = load_data()
    if df is None or df.empty:
        console.print("[yellow]분석할 데이터가 충분하지 않습니다.[/yellow]")
        return

    console.print(Rule("[bold cyan]통계 시각화[/bold cyan]"))
    choice = Prompt.ask(
        "보고 싶은 시각화 자료를 선택하세요",
        choices=['1', '2'],
        default='1'
    )

    if choice == '1':
        df_recent_7days = df[df['날짜'] >= (datetime.now() - timedelta(days=7))]
        if df_recent_7days.empty:
            console.print("[yellow]최근 7일간의 데이터가 없습니다.[/yellow]")
            return
        subject_time = df_recent_7days.groupby('과목')['공부 시간(분)'].sum()
        plt.figure(figsize=(8, 8))
        plt.pie(subject_time, labels=subject_time.index, autopct='%1.1f%%', startangle=140, textprops={'fontsize': 12})
        plt.title('최근 7일간 과목별 공부 시간 비중', fontsize=16)
        plt.show()

    elif choice == '2':
        daily_stats = df.groupby('날짜').agg(total_time=('공부 시간(분)', 'sum'), avg_concentration=('집중도', 'mean')).sort_index()
        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax1.bar(daily_stats.index, daily_stats['total_time'], color='skyblue', label='총 공부 시간(분)')
        ax1.set_xlabel('날짜'); ax1.set_ylabel('총 공부 시간(분)', color='skyblue'); ax1.tick_params(axis='y', labelcolor='skyblue')
        ax2 = ax1.twinx()
        ax2.plot(daily_stats.index, daily_stats['avg_concentration'], color='salmon', marker='o', linestyle='--', label='평균 집중도')
        ax2.set_ylabel('평균 집중도', color='salmon'); ax2.tick_params(axis='y', labelcolor='salmon'); ax2.set_ylim(0, 6)
        plt.title('날짜별 총 공부 시간 및 평균 집중도 변화 추이', fontsize=16)
        fig.tight_layout()
        plt.show()


def generate_feedback():
    """데이터를 분석하여 표 형식으로 피드백을 제공합니다. (## UI 개선)"""
    df = load_data()
    if df is None or len(df) < 3:
        console.print(Panel("[yellow]피드백을 생성하기에 데이터가 부족합니다.\n최소 3개 이상의 기록을 추가해주세요.[/yellow]", title="[bold]학습 피드백[/bold]", border_style="yellow"))
        return

    console.print(Rule("[bold cyan]학습 피드백 시스템[/bold cyan]"))
    table = Table(title="[bold]나의 학습 습관 분석 결과[/bold]", show_header=True, header_style="bold magenta")
    table.add_column("분석 항목", style="cyan", width=20)
    table.add_column("결과 및 조언")

    # 1. 집중도 분석
    avg_concentration_by_subject = df.groupby('과목')['집중도'].mean().sort_values()
    lowest_conc_subj = avg_concentration_by_subject.index[0]
    lowest_conc_val = avg_concentration_by_subject.iloc[0]
    if lowest_conc_val < 3:
        table.add_row(
            "⚠️ 집중도 취약 과목",
            f"과목 '[bold yellow]{lowest_conc_subj}[/bold yellow]'의 평균 집중도({lowest_conc_val:.1f})가 낮습니다.\n"
            f"[italic]→ 기초 개념을 복습하거나, 학습 환경을 바꿔보세요.[/italic]"
        )

    # 2. 과목별 비중 분석
    total_study_time = df['공부 시간(분)'].sum()
    subject_proportion = (df.groupby('과목')['공부 시간(분)'].sum() / total_study_time) * 100
    imbalanced_subjects = subject_proportion[subject_proportion < 10]
    if not imbalanced_subjects.empty:
        subjects_str = ", ".join([f"'[bold yellow]{s}[/bold yellow]'" for s in imbalanced_subjects.index])
        table.add_row(
            "📊 과목 불균형",
            f"과목 {subjects_str}의 학습 비중이 전체의 10% 미만입니다.\n"
            f"[italic]→ 장기적인 성장을 위해 균형 있는 학습 계획이 필요합니다.[/italic]"
        )

    # 3. 효율성 분석
    df['효율성 점수'] = df['집중도'] * df['공부 시간(분)']
    efficiency_by_subject = df.groupby('과목')['효율성 점수'].mean().sort_values(ascending=False)
    most_efficient_subject = efficiency_by_subject.index[0]
    table.add_row(
        "💡 최고 효율 과목",
        f"과목 '[bold green]{most_efficient_subject}[/bold green]'를 공부할 때 가장 높은 효율을 보입니다.\n"
        f"[italic]→ 이 과목을 공부할 때의 성공 요인(시간, 장소, 방법 등)을 다른 과목에도 적용해보세요.[/italic]"
    )
    
    if table.row_count == 0:
        console.print(Panel("[green]축하합니다! 현재 매우 균형 잡힌 학습을 하고 있습니다. 계속 유지해주세요![/green]", title="[bold]종합 분석[/bold]", border_style="green"))
    else:
        console.print(table)


def set_weekly_goal():
    """주간 공부 목표 시간을 설정합니다."""
    console.print(Rule("[bold cyan]주간 목표 설정[/bold cyan]"))
    goal_hours = FloatPrompt.ask("- 이번 주 목표 공부 시간을 입력하세요 (시간 단위)")
            
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    
    new_goal = {'주 시작일': [start_of_week.strftime('%Y-%m-%d')], '목표 시간(시간)': [goal_hours]}
    df_new_goal = pd.DataFrame(new_goal)

    if not os.path.exists(GOAL_FILE):
        df_new_goal.to_csv(GOAL_FILE, index=False, encoding='utf-8-sig')
    else:
        df_goals = pd.read_csv(GOAL_FILE, encoding='utf-8-sig')
        df_goals = df_goals[df_goals['주 시작일'] != start_of_week.strftime('%Y-%m-%d')]
        df_goals = pd.concat([df_goals, df_new_goal], ignore_index=True)
        df_goals.to_csv(GOAL_FILE, index=False, encoding='utf-8-sig')
        
    console.print(f"[bold green]✅ 이번 주 목표({goal_hours}시간)가 설정되었습니다.[/bold green]")


def check_goal_achievement():
    """주간 목표 달성률을 프로그레스 바로 보여줍니다. (## UI 개선)"""
    console.print(Rule("[bold cyan]주간 목표 달성률 확인[/bold cyan]"))
    df_study = load_data()

    if not os.path.exists(GOAL_FILE):
        console.print("[yellow]설정된 목표가 없습니다. 먼저 주간 목표를 설정해주세요.[/yellow]")
        return
        
    df_goals = pd.read_csv(GOAL_FILE, encoding='utf-8-sig')
    df_goals['주 시작일'] = pd.to_datetime(df_goals['주 시작일'])
    today = datetime.now(); start_of_week = today - timedelta(days=today.weekday())
    current_goal = df_goals[df_goals['주 시작일'].dt.date == start_of_week.date()]
    
    if current_goal.empty:
        console.print("[yellow]이번 주 목표가 설정되지 않았습니다.[/yellow]"); return

    goal_hours = current_goal['목표 시간(시간)'].iloc[0]
    study_minutes_this_week = 0
    if df_study is not None:
        this_week_data = df_study[df_study['날짜'] >= start_of_week]
        study_minutes_this_week = this_week_data['공부 시간(분)'].sum()
        
    study_hours_this_week = study_minutes_this_week / 60
    achievement_rate = (study_hours_this_week / goal_hours) * 100 if goal_hours > 0 else 0

    table = Table(show_header=False, box=None, padding=0)
    table.add_column(width=20); table.add_column()
    table.add_row("🎯 이번 주 목표", f"[bold cyan]{goal_hours:.1f}[/bold cyan] 시간")
    table.add_row("📖 현재 공부 시간", f"[bold green]{study_hours_this_week:.1f}[/bold green] 시간")
    console.print(table)
    
    console.print("\n[bold]🏆 달성률: {:.2f} %[/bold]".format(achievement_rate))
    progress = ProgressBar(total=100, completed=min(achievement_rate, 100), width=50)
    console.print(progress)


def main():
    """프로그램의 메인 루프를 실행합니다. (## UI 개선)"""
    setup_korean_font()
    
    while True:
        console.print(Panel(
            "[bold]1.[/bold] 공부 기록 추가\n"
            "[bold]2.[/bold] 통계 및 시각화 보기\n"
            "[bold]3.[/bold] 학습 피드백 받기\n"
            "[bold]4.[/bold] 주간 목표 설정\n"
            "[bold]5.[/bold] 주간 목표 달성률 확인\n"
            "[bold]6.[/bold] 프로그램 종료",
            title="📊 [bold green]학습 관리 및 분석 프로그램[/bold green] 📊",
            subtitle="원하는 기능의 번호를 입력하세요",
            border_style="blue"
        ))
        
        choice = Prompt.ask("선택", choices=['1', '2', '3', '4', '5', '6'])

        if choice == '1': add_study_record()
        elif choice == '2': show_visualizations()
        elif choice == '3': generate_feedback()
        elif choice == '4': set_weekly_goal()
        elif choice == '5': check_goal_achievement()
        elif choice == '6':
            console.print("[bold magenta]프로그램을 종료합니다. 꾸준한 학습을 응원합니다! 💪[/bold magenta]")
            break

if __name__ == "__main__":
    main()