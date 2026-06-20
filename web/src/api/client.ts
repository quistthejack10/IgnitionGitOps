// Minimal API client pointed at the gateway (proxied in dev via vite.config.ts).
// Replaced/extended with a typed GraphQL client once the model-generated schema exists (M2).

export async function gql<T>(query: string, variables?: Record<string, unknown>): Promise<T> {
  const res = await fetch("/graphql", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, variables }),
  });
  const body = await res.json();
  if (body.errors) throw new Error(JSON.stringify(body.errors));
  return body.data as T;
}

export async function health(): Promise<{ status: string }> {
  return (await fetch("/api/v1/")).json();
}
