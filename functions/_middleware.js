export async function onRequest(context) {
    const target = new URL(
        "https://stockversity-de4efc1c.appliedintelligencecorporation.com"
    );

    const incoming = new URL(context.request.url);

    target.pathname = incoming.pathname;
    target.search = incoming.search;

    const request = new Request(target.toString(), context.request);

    return fetch(request);
}
