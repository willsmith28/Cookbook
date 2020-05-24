const uniqueFieldInList = field => list => {
  const fieldValues = new Set();
  for (const item in list) {
    if (Object.prototype.hasOwnProperty.call(item, field)) {
      const value = item[field];
      if (value && fieldValues.has(value)) {
        return false;
      }
      fieldValues.add(value);
    }
  }
  return true;
};

export default uniqueFieldInList;
