module.exports = {
  async query(sql) {
    console.log(sql);
    return [{ id: 1, role: 'admin' }];
  }
};
