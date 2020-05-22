import axios from "axios";
import router from "../router";
import store from "../store";

const client = axios.create({
  baseURL: "http://127.0.0.1:8000/api",
  "Access-Control-Allow-Origin": "*",
  headers: {
    post: { "Content-Type": "application/json" },
    put: { "Content-Type": "application/json" }
  }
});

const refreshTokenOnUnAuthorized = error => {
  if (error.response.status === 401) {
    if (error.config.url.includes("/token/refresh")) {
      router.push({ name: "login" });
      return Promise.reject(error);
    }
    return store
      .dispatch("user/refreshToken")
      .then(() => {
        const { config: originalRequest } = error;
        return axios(originalRequest);
      })
      .catch(error => Promise.reject(error));
  }
  return Promise.reject(error);
};

const responseSuccessInterceptor = response => response;

client.interceptors.response.use(
  responseSuccessInterceptor,
  refreshTokenOnUnAuthorized
);

export default client;
