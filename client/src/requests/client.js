import axios from "axios";
import store from "../store";

const client = axios.create({
  baseURL: `http://${location.hostname}:1337/api`,
  "Access-Control-Allow-Origin": "*",
  headers: {
    post: { "Content-Type": "application/json" },
    put: { "Content-Type": "application/json" }
  }
});

const refreshTokenOnUnAuthorized = async error => {
  const { config: originalRequest } = error;
  if (
    error.response.status !== 401 ||
    originalRequest.url.includes("api/token/refresh") ||
    originalRequest.url.includes("api/token/logout") ||
    originalRequest._retry
  ) {
    return Promise.reject(error);
  }

  try {
    await store.dispatch("user/refreshToken");
  } catch (error) {
    return Promise.reject(error);
  }

  originalRequest._retry = true;
  return axios(originalRequest);
};

client.interceptors.response.use(
  response => response,
  refreshTokenOnUnAuthorized
);

export default client;
