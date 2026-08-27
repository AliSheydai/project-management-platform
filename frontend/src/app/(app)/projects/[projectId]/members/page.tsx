import { MembersView } from "@/components/members/members-view";

export default async function ProjectMembersPage({
  params,
}: {
  params: Promise<{ projectId: string }>;
}) {
  const { projectId } = await params;
  return <MembersView projectId={projectId} />;
}
