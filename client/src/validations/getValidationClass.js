export default (fieldName, $field) => {
  const { [fieldName]: field } = $field;
  if (field) {
    return { "md-invalid": field.$invalid && field.$dirty };
  }
};
