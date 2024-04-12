// Loop over input items and add a new field called 'myNewField' to the JSON of each one
const res = [];
for (const item of $input.all()) {
  if (item.json.message.content) {
    try {
      res.push(item.json.message.content);
    } catch {
      res.push({
        orders: [],
        total: 0,
      });
    }
  } else {
    res.push({
      orders: [],
      total: 0,
    });
  }
}

for (const item of res) {
  if ("multiple_choices" in item) {
    let line_message = {
      type: "bubble",
      body: {
        type: "box",
        layout: "vertical",
        contents: [
          {
            type: "text",
            text: "您詢問的商品有幾個不同的選擇，請問你要的是哪種呢？",
            weight: "regular",
            size: "sm",
            wrap: true,
          },
        ],
      },
      footer: {
        type: "box",
        layout: "vertical",
        spacing: "sm",
        contents: [
          {
            type: "button",
            action: {
              type: "postback",
              label: "都不是",
              data: "choose_others",
            },
          },
        ],
        flex: 0,
      },
    };
    for (const choice of item["multiple_choices"]) {
      let total = choice["unit_price"] * choice["quantity"];
      line_message["body"]["contents"].push({
        type: "button",
        action: {
          type: "message",
          label:
            choice["item"] +
            " " +
            choice["quantity"] +
            choice["unit"] +
            "(" +
            total +
            ")",
          text: choice["item"] + " " + choice["quantity"] + choice["unit"],
        },
      });
      item["message"] = line_message;
      item["alt_message"] = "請問您是要訂購的是 ...";
    }
  } else {
    let line_message = {
      type: "bubble",
      header: {
        type: "box",
        layout: "vertical",
        contents: [
          {
            type: "text",
            text: "請問您是要訂購:",
          },
        ],
      },
      body: {
        type: "box",
        layout: "vertical",
        contents: [],
      },
      footer: {
        type: "box",
        layout: "horizontal",
        spacing: "sm",
        contents: [
          {
            type: "button",
            style: "link",
            height: "sm",
            action: {
              type: "postback",
              label: "確認",
              data: "confirm_order " + item["message_id"],
            },
          },
          {
            type: "button",
            style: "link",
            height: "sm",
            action: {
              type: "postback",
              label: "取消",
              data: "cancel_order " + item["message_id"],
            },
          },
        ],
        flex: 0,
      },
    };
    for (const order of item["orders"]) {
      let text = order["item"];
      if (order["quantity"]) {
        text += " x" + order["quantity"];
        if (order["unit"]) {
          text += order["unit"];
        }
      } else if (order["units"]) {
        text += " x" + order["units"];
        if (order["unit"]) {
          text += order["unit"];
        }
      }
      if (order["subtotal"]) {
        text += ", 價格: " + order["subtotal"];
      }
      line_message["body"]["contents"].push({
        type: "text",
        wrap: true,
        size: "sm",
        text: text,
      });
    }
    if (item["orders"].length > 0) {
      line_message["body"]["contents"].push({
        type: "separator",
      });
      line_message["body"]["contents"].push({
        type: "text",
        text: "總價: " + item["total"],
      });
    }
    item["message"] = line_message;
    item["alt_message"] = "請問您是要訂購的是 ...";
  }
}

return res;
