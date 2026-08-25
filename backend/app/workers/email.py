from typing import Any

from app.core.logging import logger


def render_email_template(
    template_name: str,
    context: dict[str, Any],
) -> tuple[str, str]:
    """Generate subject and plain-text/html body from named template."""
    if template_name == "welcome":
        user_name = context.get("name", "there")
        subject = "Welcome to Project Management Platform!"
        body = (
            f"Hi {user_name},\n\n"
            f"Welcome to your modern workspace. You can now create projects, "
            f"manage tasks, track progress in real-time, and collaborate.\n\n"
            f"Best regards,\nThe Project Management Team"
        )
    elif template_name == "task_assigned":
        task_title = context.get("task_title", "a task")
        project_name = context.get("project_name", "your project")
        assigner = context.get("assigner_name", "A team member")
        subject = f"Task Assigned: {task_title}"
        body = (
            f"Hello,\n\n"
            f"{assigner} assigned you to '{task_title}' in '{project_name}'.\n\n"
            f"Log in to your dashboard to view the details and update progress.\n\n"
            f"Best regards,\nThe Project Management Team"
        )
    elif template_name == "user_mentioned":
        mentioner = context.get("mentioner_name", "Someone")
        task_title = context.get("task_title", "a task")
        comment_text = context.get("comment_text", "")
        subject = f"Mentioned in: {task_title}"
        body = (
            f"Hello,\n\n"
            f"{mentioner} mentioned you in a comment on task '{task_title}':\n\n"
            f"> {comment_text}\n\n"
            f"Best regards,\nThe Project Management Team"
        )
    elif template_name == "project_invited":
        inviter = context.get("inviter_name", "A project administrator")
        project_name = context.get("project_name", "a project")
        role = context.get("role", "MEMBER")
        subject = f"Invitation to join project: {project_name}"
        body = (
            f"Hello,\n\n"
            f"{inviter} invited you to join '{project_name}' as a {role}.\n\n"
            f"Log in to start collaborating.\n\n"
            f"Best regards,\nThe Project Management Team"
        )
    else:
        subject = context.get("subject", "Notification")
        body = context.get("message", "You have a new notification.")

    return subject, body


async def send_email(
    to_email: str,
    subject: str,
    body: str,
) -> bool:
    """Simulate or execute transactional email dispatch."""
    logger.info(
        "Email delivered to %s | Subject: %s | Preview: %s",
        to_email,
        subject,
        body[:80].replace("\n", " "),
    )
    return True
