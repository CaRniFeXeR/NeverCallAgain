export default class Call {
  constructor(
    title,
    state,
    receiverName,
    receiverPhonenr,
    initiatorName,
    possibleDatetimes,
    result = null
  ) {
    this.title = title;
    this.state = state;
    this.receiverName = receiverName;
    this.receiverPhonenr = receiverPhonenr;
    this.initiatorName = initiatorName;
    this.possibleDatetimes = possibleDatetimes;
    this.result = result;
  }

  setResult(result) {
    this.result = result;
  }
}
