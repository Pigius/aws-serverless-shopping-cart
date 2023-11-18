import { Auth, API } from "aws-amplify";

async function getHeaders() {
  const headers = {
    "Content-Type": "application/json",
  };

  let session = null;
  try {
    session = await Auth.currentSession();
  } catch (e) {
    console.error("Error getting current session:", e);
  }

  if (session) {
    let authHeader = session.getIdToken().jwtToken;
    headers["Authorization"] = authHeader;
  }
  return headers;
}

export async function getProducts() {
  return getHeaders().then((headers) =>
    API.get("ProductAPI", "/product", {
      headers: headers,
      withCredentials: true,
    })
  );
}
