export default class Call {
  constructor(
    title,
    state,
    receiverName,
    receiverPhonenr,
    initiatorName,
    possibleDatetimes
  ) {
    this.title = title;
    this.state = state;
    this.receiverName = receiverName;
    this.receiverPhonenr = receiverPhonenr;
    this.initiatorName = initiatorName;
    this.possibleDatetimes = possibleDatetimes;
  }
}
