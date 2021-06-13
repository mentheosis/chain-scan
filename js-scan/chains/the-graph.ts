const https = require('https')

const query = `{
  loans(where: {opened_gt: 0, closed: null, debt_gt: 0}) {
    id
    opened
    closed
    debt
  }
}`

const options = {
  hostname: 'https://api.thegraph.com',
  port: 443,
  path: '/subgraphs/name/centrifuge/tinlake',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': query.length,
    'Accept': 'application/json',
  },
}

console.log("sending")
const req = https.request(options, res => {
  console.log(`statusCode: ${res.statusCode}`)
  res.on('data', d => {
    console.log("got result", d)
  })
})

req.on('error', error => {
  console.error("error....",error)
})

req.write(query)
req.end()
console.log("done")