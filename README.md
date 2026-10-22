# Class Artifacts

A template for instructors who want to add one in-lecture activity per module that produces an **artifact** students attach to the discussion post they already write. The framework behind it is called *One Module, One Activity*. It works for 14-week semesters and 6-week summer terms, for any subject, with or without technology.

> Keep your learning objectives, lectures and discussion posts. Add one activity that generates an artifact.

Live example: [met-ad-599.github.io](https://met-ad-599.github.io/) (MET AD 599, Python and SQL for Business Analytics, Fall 2026).

## What you add, and what you already have

| Piece | Already in your course? | What changes |
|---|---|---|
| Learning objectives | Yes | Nothing. The activity practices an objective you already teach. |
| Lecture | Yes | No content changes. Make room for one activity segment. |
| **Activity and artifact** | **New** | **Students build one artifact: a written answer, a table, a diagram, a code snippet, a short decision memo.** |
| Discussion post | Yes | Link the prompt to the activity and ask students to attach the artifact. |

## The student rhythm

| Step | Where | What students do |
|---|---|---|
| **Learn** | During the lecture | Learn the concepts through the lecture content. |
| **Comprehend** | During the lecture | Try it out in the activity and generate an artifact. |
| **Demonstrate** | Discussion board | Submit the artifact in the discussion and compare with the class. |
| **Apply** | Beyond the module | Use it in future lessons, assignments, the term project and the real world. |

Students who miss the live session do the same activity from the recording and submit the same artifact. Only the timing changes.

## Start here

1. **Read the framework** (5 minutes): [docs/01-framework.md](docs/01-framework.md)
2. **Map your course** with the 14-week or 6-week plan: [docs/02-plan-your-course.md](docs/02-plan-your-course.md)
3. **Design one activity** with the worksheet: [templates/activity-template.md](templates/activity-template.md)
4. **Add one line to your discussion prompt**: [docs/04-discussion-prompts.md](docs/04-discussion-prompts.md)
5. **Pick how you will run it**:
   - No technology: [docs/05-low-tech-techniques.md](docs/05-low-tech-techniques.md)
   - A form tool you already have (Microsoft Forms, Google Forms, your LMS quiz tool): [docs/05-low-tech-techniques.md#form-tools](docs/05-low-tech-techniques.md#form-tools)
   - The Python starter web app in this repo: [docs/06-starter-web-app.md](docs/06-starter-web-app.md)

Start with one module. You do not need all six to begin.

## What is in this repo

| Path | What it is |
|---|---|
| `docs/` | The framework, course plans, activity design, discussion prompts, low-tech techniques, the web app |
| `templates/` | Fill-in worksheets: activity, discussion prompt, 14-week plan, 6-week plan |
| `examples/ad599/` | A complete worked example: six modules, six artifacts, and how one activity feeds Discussion 2 |
| `starter-app/` | A small Python (Flask) web app: roster login, activities defined in one config file, a unique input per student, an artifact card students can attach, and a live class view for the instructor |

## Use this template

At the top of [this repo](https://github.com/BostonAnalytics/class-artifacts), click **Use this template** to make your own copy, then edit `templates/` and, if you want the web app, `starter-app/course.py`. Nothing here contains student data.

## Contact

Sree Kumar Valath, Boston University Metropolitan College. Questions and improvements: open an issue on this repo.
