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

const getAccessToken = () => localStorage.getItem("access");
const getRefreshToken = () => localStorage.getItem("refresh");

const authInterceptor = config => {
  const token = getAccessToken();

  config.headers["Authorization"] = token
    ? `Authorization: Bearer ${token}`
    : "";

  return config;
};

const refreshTokenOnUnAuthorized = error => {
  const refreshToken = getRefreshToken();
  if (!refreshToken || error.response.status !== 401) {
    return Promise.reject(error);
  }
  if (error.config.url.includes("/token/refresh")) {
    router.push({ name: "home" });
    return Promise.reject(error);
  }
  const { config: originalRequest } = error;
  if (refreshToken) {
    return client
      .post("/token/refresh/", { refreshToken })
      .then(({ data }) => {
        localStorage.setItem("access", data.access);
        originalRequest.headers[
          "Authorization"
        ] = `Authorization: Bearer ${data.access}`;
        return axios(originalRequest);
      })
      .catch(error => {
        console.log(error);
      });
  }
  return Promise.reject(error);
};

const responseSuccessInterceptor = response => response;
const requestErrorInterceptor = error => Promise.reject(error);

client.interceptors.request.use(authInterceptor, requestErrorInterceptor);
client.interceptors.response.use(
  responseSuccessInterceptor,
  refreshTokenOnUnAuthorized
);

export default client;
