BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);


CREATE TABLE users (
    id UUID NOT NULL, 
    email VARCHAR(255) NOT NULL, 
    password_hash VARCHAR(255) NOT NULL, 
    first_name VARCHAR(100) NOT NULL, 
    last_name VARCHAR(100) NOT NULL, 
    avatar_url VARCHAR(500), 
    is_active BOOLEAN DEFAULT true NOT NULL, 
    is_superuser BOOLEAN DEFAULT false NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (email)
);

CREATE INDEX ix_users_id ON users (id);

CREATE UNIQUE INDEX ix_users_email ON users (email);

CREATE TABLE refresh_tokens (
    id UUID NOT NULL, 
    user_id UUID NOT NULL, 
    token_hash VARCHAR(255) NOT NULL, 
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL, 
    is_revoked BOOLEAN DEFAULT false NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
    UNIQUE (token_hash)
);

CREATE INDEX ix_refresh_tokens_id ON refresh_tokens (id);

CREATE INDEX ix_refresh_tokens_user_id ON refresh_tokens (user_id);

CREATE UNIQUE INDEX ix_refresh_tokens_token_hash ON refresh_tokens (token_hash);

CREATE INDEX ix_refresh_tokens_expires_at ON refresh_tokens (expires_at);

INSERT INTO alembic_version (version_num) VALUES ('0001_initial_schema') RETURNING alembic_version.version_num;


CREATE TABLE projects (
    id UUID NOT NULL, 
    name VARCHAR(150) NOT NULL, 
    description TEXT, 
    owner_id UUID NOT NULL, 
    is_archived BOOLEAN DEFAULT false NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(owner_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX ix_projects_id ON projects (id);

CREATE INDEX ix_projects_name ON projects (name);

CREATE INDEX ix_projects_owner_id ON projects (owner_id);

CREATE TABLE project_members (
    id UUID NOT NULL, 
    project_id UUID NOT NULL, 
    user_id UUID NOT NULL, 
    role VARCHAR(20) DEFAULT 'MEMBER' NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE, 
    FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
    CONSTRAINT uq_project_member UNIQUE (project_id, user_id)
);

CREATE INDEX ix_project_members_id ON project_members (id);

CREATE INDEX ix_project_members_project_id ON project_members (project_id);

CREATE INDEX ix_project_members_user_id ON project_members (user_id);

CREATE INDEX ix_project_members_role ON project_members (role);

UPDATE alembic_version SET version_num='0002_projects_and_rbac' WHERE alembic_version.version_num = '0001_initial_schema';


CREATE TABLE tasks (
    id UUID NOT NULL, 
    project_id UUID NOT NULL, 
    title VARCHAR(200) NOT NULL, 
    description TEXT, 
    status VARCHAR(20) DEFAULT 'TODO' NOT NULL, 
    priority VARCHAR(20) DEFAULT 'MEDIUM' NOT NULL, 
    assignee_id UUID, 
    creator_id UUID NOT NULL, 
    due_date TIMESTAMP WITH TIME ZONE, 
    position FLOAT DEFAULT '1000.0' NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(assignee_id) REFERENCES users (id) ON DELETE SET NULL, 
    FOREIGN KEY(creator_id) REFERENCES users (id) ON DELETE CASCADE, 
    FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE
);

CREATE INDEX ix_tasks_id ON tasks (id);

CREATE INDEX ix_tasks_project_id ON tasks (project_id);

CREATE INDEX ix_tasks_title ON tasks (title);

CREATE INDEX ix_tasks_status ON tasks (status);

CREATE INDEX ix_tasks_priority ON tasks (priority);

CREATE INDEX ix_tasks_assignee_id ON tasks (assignee_id);

CREATE INDEX ix_tasks_creator_id ON tasks (creator_id);

CREATE INDEX ix_tasks_due_date ON tasks (due_date);

CREATE INDEX ix_tasks_position ON tasks (position);

UPDATE alembic_version SET version_num='0003_tasks_schema' WHERE alembic_version.version_num = '0002_projects_and_rbac';


CREATE TABLE comments (
    id UUID NOT NULL, 
    task_id UUID NOT NULL, 
    author_id UUID NOT NULL, 
    content TEXT NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(author_id) REFERENCES users (id) ON DELETE CASCADE, 
    FOREIGN KEY(task_id) REFERENCES tasks (id) ON DELETE CASCADE
);

CREATE INDEX ix_comments_id ON comments (id);

CREATE INDEX ix_comments_task_id ON comments (task_id);

CREATE INDEX ix_comments_author_id ON comments (author_id);

CREATE INDEX ix_comments_created_at ON comments (created_at);

CREATE TABLE activity_logs (
    id UUID NOT NULL, 
    project_id UUID NOT NULL, 
    task_id UUID, 
    user_id UUID NOT NULL, 
    action VARCHAR(50) NOT NULL, 
    entity_type VARCHAR(50) NOT NULL, 
    entity_id UUID NOT NULL, 
    details JSON, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE, 
    FOREIGN KEY(task_id) REFERENCES tasks (id) ON DELETE CASCADE, 
    FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX ix_activity_logs_id ON activity_logs (id);

CREATE INDEX ix_activity_logs_project_id ON activity_logs (project_id);

CREATE INDEX ix_activity_logs_task_id ON activity_logs (task_id);

CREATE INDEX ix_activity_logs_user_id ON activity_logs (user_id);

CREATE INDEX ix_activity_logs_action ON activity_logs (action);

CREATE INDEX ix_activity_logs_entity_type ON activity_logs (entity_type);

CREATE INDEX ix_activity_logs_entity_id ON activity_logs (entity_id);

CREATE INDEX ix_activity_logs_created_at ON activity_logs (created_at);

UPDATE alembic_version SET version_num='0004_comments_and_activity' WHERE alembic_version.version_num = '0003_tasks_schema';


CREATE TABLE labels (
    id UUID NOT NULL, 
    project_id UUID NOT NULL, 
    name VARCHAR(50) NOT NULL, 
    color VARCHAR(20) DEFAULT '#6B7280' NOT NULL, 
    description VARCHAR(200), 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE, 
    CONSTRAINT uq_project_label_name UNIQUE (project_id, name)
);

CREATE INDEX ix_labels_id ON labels (id);

CREATE INDEX ix_labels_project_id ON labels (project_id);

CREATE INDEX ix_labels_name ON labels (name);

CREATE TABLE task_labels (
    task_id UUID NOT NULL, 
    label_id UUID NOT NULL, 
    PRIMARY KEY (task_id, label_id), 
    FOREIGN KEY(label_id) REFERENCES labels (id) ON DELETE CASCADE, 
    FOREIGN KEY(task_id) REFERENCES tasks (id) ON DELETE CASCADE
);

CREATE INDEX ix_task_labels_task_id ON task_labels (task_id);

CREATE INDEX ix_task_labels_label_id ON task_labels (label_id);

ALTER TABLE tasks ADD COLUMN custom_fields JSON;

UPDATE alembic_version SET version_num='0005_labels_and_metadata' WHERE alembic_version.version_num = '0004_comments_and_activity';


CREATE TABLE attachments (
    id UUID NOT NULL, 
    task_id UUID NOT NULL, 
    uploader_id UUID NOT NULL, 
    file_name VARCHAR(255) NOT NULL, 
    file_path VARCHAR(500) NOT NULL, 
    file_size BIGINT NOT NULL, 
    content_type VARCHAR(100) NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(task_id) REFERENCES tasks (id) ON DELETE CASCADE, 
    FOREIGN KEY(uploader_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX ix_attachments_id ON attachments (id);

CREATE INDEX ix_attachments_task_id ON attachments (task_id);

CREATE INDEX ix_attachments_uploader_id ON attachments (uploader_id);

CREATE INDEX ix_attachments_created_at ON attachments (created_at);

UPDATE alembic_version SET version_num='0006_attachments_schema' WHERE alembic_version.version_num = '0005_labels_and_metadata';


CREATE TABLE saved_views (
    id UUID NOT NULL, 
    user_id UUID NOT NULL, 
    project_id UUID, 
    name VARCHAR(100) NOT NULL, 
    filters JSON NOT NULL, 
    is_default BOOLEAN DEFAULT false NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE CASCADE, 
    FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX ix_saved_views_id ON saved_views (id);

CREATE INDEX ix_saved_views_user_id ON saved_views (user_id);

CREATE INDEX ix_saved_views_project_id ON saved_views (project_id);

UPDATE alembic_version SET version_num='0007_search_and_saved_views' WHERE alembic_version.version_num = '0006_attachments_schema';


CREATE TABLE notifications (
    id UUID NOT NULL, 
    user_id UUID NOT NULL, 
    actor_id UUID, 
    type VARCHAR(50) NOT NULL, 
    title VARCHAR(200) NOT NULL, 
    message TEXT NOT NULL, 
    entity_type VARCHAR(50) NOT NULL, 
    entity_id UUID NOT NULL, 
    payload JSON, 
    is_read BOOLEAN DEFAULT false NOT NULL, 
    read_at TIMESTAMP WITH TIME ZONE, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(actor_id) REFERENCES users (id) ON DELETE SET NULL, 
    FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX ix_notifications_id ON notifications (id);

CREATE INDEX ix_notifications_user_id ON notifications (user_id);

CREATE INDEX ix_notifications_actor_id ON notifications (actor_id);

CREATE INDEX ix_notifications_type ON notifications (type);

CREATE INDEX ix_notifications_entity_type ON notifications (entity_type);

CREATE INDEX ix_notifications_entity_id ON notifications (entity_id);

CREATE INDEX ix_notifications_is_read ON notifications (is_read);

CREATE INDEX ix_notifications_created_at ON notifications (created_at);

UPDATE alembic_version SET version_num='0008_notifications_schema' WHERE alembic_version.version_num = '0007_search_and_saved_views';

COMMIT;

