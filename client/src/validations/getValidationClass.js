export default (fieldName, $data) => {
  const { [fieldName]: field } = $data;
  if (field) {
    return { "md-invalid": field.$invalid && field.$dirty };
  }
};
