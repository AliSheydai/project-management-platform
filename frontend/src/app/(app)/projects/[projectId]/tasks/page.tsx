import { Suspense } from "react";
import { TasksView } from "@/components/tasks/tasks-view";
import { LoadingSkeleton } from "@/components/shared";
import { PageContainer } from "@/components/layout/page-container";

export default async function ProjectTasksPage({
  params,
}: {
  params: Promise<{ projectId: string }>;
}) {
  const { projectId } = await params;
  return (
    <Suspense
      fallback={
        <PageContainer>
          <LoadingSkeleton count={5} />
        </PageContainer>
      }
    >
      <TasksView projectId={projectId} />
    </Suspense>
  );
}
