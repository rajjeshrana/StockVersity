export async function onRequest(context) {
    const incoming = new URL(context.request.url);

    const target = new URL(incoming.pathname.startsWith("/api/futures") ? "https://api.stockversity.in" : "https://stockversity-de4efc1c.appliedintelligencecorporation.com");

    target.pathname = incoming.pathname;
    target.search = incoming.search;

    const request = new Request(target.toString(), context.request);
    return fetch(request);
}
