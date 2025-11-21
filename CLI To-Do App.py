#!/usr/bin/env python3
import argparse
import json
import os
from dataclasses import dataclass, asdict
from typing import List

DATA_FILE = "tasks.json"


@dataclass
class Task:
    id: int
    title: str
    done: bool = False


# ---------- 저장소 레이어 ----------

def load_tasks() -> List[Task]:
    """저장된 할 일 목록을 JSON 파일에서 불러옵니다."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
        # JSON 데이터를 Task 객체 목록으로 변환
        return [Task(**item) for item in raw]
    except (json.JSONDecodeError, FileNotFoundError):
        # 파일이 비어있거나 형식이 잘못된 경우 빈 목록 반환
        return []


def save_tasks(tasks: List[Task]) -> None:
    """할 일 목록을 JSON 파일에 저장합니다."""
    # Task 객체 목록을 딕셔너리 목록으로 변환하여 저장
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([asdict(t) for t in tasks], f, ensure_ascii=False, indent=2)


def next_task_id(tasks: List[Task]) -> int:
    """새 할 일에 사용할 다음 ID를 계산합니다."""
    if not tasks:
        return 1
    # 현재 존재하는 ID 중 최댓값 + 1
    return max(t.id for t in tasks) + 1


# ---------- 유스케이스 레이어 ----------

def add_task(title: str) -> Task:
    """새로운 할 일을 추가합니다."""
    tasks = load_tasks()
    task = Task(id=next_task_id(tasks), title=title, done=False)
    tasks.append(task)
    save_tasks(tasks)
    return task


def list_tasks(show_all: bool = True) -> List[Task]:
    """할 일 목록을 조회합니다. show_all이 False면 미완료된 항목만 보여줍니다."""
    tasks = load_tasks()
    if show_all:
        return tasks
    return [t for t in tasks if not t.done]


def complete_task(task_id: int) -> Task:
    """특정 ID의 할 일을 완료 처리합니다."""
    tasks = load_tasks()
    for t in tasks:
        if t.id == task_id:
            t.done = True
            save_tasks(tasks)
            return t
    raise ValueError(f"오류: 할 일 ID {task_id}를 찾을 수 없습니다.")


def delete_task(task_id: int) -> None:
    """특정 ID의 할 일을 삭제합니다."""
    tasks = load_tasks()
    new_tasks = [t for t in tasks if t.id != task_id]
    if len(new_tasks) == len(tasks):
        raise ValueError(f"오류: 할 일 ID {task_id}를 찾을 수 없습니다.")
    save_tasks(new_tasks)


def clear_completed() -> int:
    """완료된 모든 할 일을 목록에서 삭제합니다."""
    tasks = load_tasks()
    new_tasks = [t for t in tasks if not t.done]
    removed = len(tasks) - len(new_tasks)
    save_tasks(new_tasks)
    return removed


# ---------- CLI 레이어 ----------

def build_parser() -> argparse.ArgumentParser:
    """명령줄 인수를 처리하기 위한 ArgumentParser를 구성합니다."""
    parser = argparse.ArgumentParser(
        prog="python todo.py",
        description="간단한 CLI TODO 앱 (add, list, done, delete).",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # add 명령어
    p_add = subparsers.add_parser("add", help="할 일 추가")
    p_add.add_argument("title", type=str, help="추가할 할 일 내용")

    # list 명령어
    p_list = subparsers.add_parser("list", help="할 일 목록 조회")
    p_list.add_argument(
        "--all",
        action="store_true",
        help="완료된 항목까지 모두 보기",
    )

    # done 명령어
    p_done = subparsers.add_parser("done", help="할 일 완료 처리")
    p_done.add_argument("id", type=int, help="완료 처리할 할 일 ID")

    # delete 명령어
    p_del = subparsers.add_parser("delete", help="할 일 삭제")
    p_del.add_argument("id", type=int, help="삭제할 할 일 ID")

    # clear-completed 명령어
    subparsers.add_parser("clear-completed", help="완료된 할 일 모두 삭제")

    return parser


def main() -> None:
    """애플리케이션의 메인 진입점입니다."""
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "add":
            task = add_task(args.title)
            print(f"[추가] #{task.id}: {task.title}")

        elif args.command == "list":
            tasks = list_tasks(show_all=args.all)
            if not tasks:
                print("등록된 할 일이 없습니다.")
                return

            print("=== TODO 리스트 ===")
            for t in tasks:
                status = "✅" if t.done else "⏳"
                print(f"{t.id:3d} {status} {t.title}")

        elif args.command == "done":
            task = complete_task(args.id)
            print(f"[완료] #{task.id}: {task.title}")

        elif args.command == "delete":
            delete_task(args.id)
            print(f"[삭제] #{args.id}")

        elif args.command == "clear-completed":
            removed = clear_completed()
            print(f"[정리] 완료된 할 일 {removed}개 삭제")
            
    except ValueError as e:
        print(str(e))
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")


if __name__ == "__main__":
    main()