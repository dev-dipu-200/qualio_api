# services/graphql_queries.py
"""GraphQL queries for Qualia API."""
# queries
GET_ORDERS_QUERY = """
query orders($input: OrdersInput) {
    orders(input: $input) {
        orders {
            _id
            product_name
            product_description
            product_type
            product_turn_time
            vertical
            order_number
            purpose
            customer_name
            customer_order_number
            customer_id
            customer_order_id
            status
            status_details {
                open
                pending
                accepted
                declined
                cancelled
                submitted
                revision_required
                completed
                resubmitted
                resubmission_accepted
                preorder
                cancellation_reason
                cancelled_by
                revision_required_reason
                created_date
                closed_date
            }
            quoted_price
            quoted_qualia_fee
            price
            cancellation_amount
            pay_on_close
            charged_at_beginning
            due_date
            projected_close_date
            properties {
                address_1
                address_2
                city
                state
                zipcode
                county
                flat_address
            }
            credentials {
                placeholder
            }
        }
    }
}
"""

GET_ORDER_QUERY = """
query GetOrder($input: ID!) {
  order(_id: $input) {
    order {
      _id
      product_name
      product_description
      product_type
      product_turn_time
      vertical
      order_number
      purpose
      transaction_type
      purchase_price_amount
      loan_amount
      loan_type
      cash_only
      customer_name
      customer_organization_name
      customer_order_number
      customer_contact {
        name
        phone
        email
      }
      settlement_agency_address {
        address_1
        address_2
        zipcode
        city
        state
        county
        flat_address
      }
      settlement_agency_id
      lender_name
      customer_id
      customer_deployment
      customer_order_id
      status
      status_details {
        open
        pending
        accepted
        declined
        cancelled
        submitted
        revision_required
        completed
        resubmitted
        resubmission_accepted
        cancellation_reason
        cancelled_by
        revision_required_reason
        created_date
        closed_date
      }
      quoted_price
      quoted_qualia_fee
      price
      product_units
      cancellation_amount
      pay_on_close
      charged_at_beginning
      due_date
      projected_close_date
      disbursement_date
      additional_costs {
        name
        cost_per_unit
        units
        is_discount
        is_percentage_of_total
        percentage
      }
      addon_costs {
        name
        cost_per_unit
        units
      }
      primary_document {
        _id
        name
        url
        tag
      }
      additional_documents {
        _id
        name
        url
        tag
      }
      borrowers {
        full_name
        first_name
        middle_name
        last_name
        spouse_full_name
        spouse_first_name
        spouse_middle_name
        spouse_last_name
        spouse_on_title
        spouse_on_loan
        type
        current_address {
          address_1
          address_2
          zipcode
          city
          state
          county
          flat_address
        }
        forwarding_address {
          address_1
          address_2
          zipcode
          city
          state
          county
          flat_address
        }
        vesting
        phone
        cell_phone
        work_phone
        home_phone
        email
      }
      sellers {
        full_name
        first_name
        middle_name
        last_name
        spouse_full_name
        spouse_first_name
        spouse_middle_name
        spouse_last_name
        spouse_on_title
        spouse_on_loan
        type
        current_address {
          address_1
          address_2
          zipcode
          city
          state
          county
          flat_address
        }
        forwarding_address {
          address_1
          address_2
          zipcode
          city
          state
          county
          flat_address
        }
        vesting
        phone
        cell_phone
        work_phone
        home_phone
        email
      }
      customer_files {
        _id
        name
        url
        tag
      }
      activities {
        _id
        order_id
        created_date
        description
        customer_name
        activity_type
        order_number
      }
      parent_id
      credentials {
        placeholder
      }
      underwriter
      resware_mapped_ids {
        transaction_type
        product
        customer
      }
      third_party_order_number
      fees {
        name
        amount
        is_prorated
        proration_data {
          paid_thru
          next_due
          payment_schedule
          installment_amount
          installment_start_date
          installment_end_date
          proration_date
        }
        payor
        payee
        payee_address {
          address_1
          address_2
          zipcode
          city
          state
          county
          flat_address
        }
      }
      custom_fields {
        name
        type
        boolean_value
        string_value
        document_value
        document_label
        money_value
        date_value
      }
    }
    outstanding_tasks
  }
}
"""

GET_MESSAGES_LIST_QUERY = """
query Messages {
    messages {
        order_id
        message_id
        order_number
        from_name
        read
        text
        created_date
        attachments {
            _id
            name
            url
            tag
        }
    }
}
"""



# mutations
ACCEPT_ORDER_MUTATION = """
mutation acceptOrder($input: AcceptOrderInput) {
  acceptOrder(input: $input) {
    status
    status_details {
      open
      pending
      accepted
      declined
      cancelled
      submitted
      revision_required
      completed
      resubmitted
      resubmission_accepted
      preorder
      cancellation_reason
      cancelled_by
      revision_required_reason
      created_date
      closed_date
    }
  }
}
"""

CANCEL_ORDER_MUTATION = """
mutation cancelOrder($input: CancelOrderInput) {
  cancelOrder(input: $input) {
    status
    status_details {
      open
      pending
      accepted
      declined
      cancelled
      submitted
      revision_required
      completed
      resubmitted
      resubmission_accepted
      preorder
      cancellation_reason
      cancelled_by
      revision_required_reason
      created_date
      closed_date
    }
  }
}
"""

DECLINE_ORDER_MUTATION = """
mutation declineOrder($input: DeclineOrderInput) {
  declineOrder(input: $input) {
    status
    status_details {
      open
      pending
      accepted
      declined
      cancelled
      submitted
      revision_required
      completed
      resubmitted
      resubmission_accepted
      preorder
      cancellation_reason
      cancelled_by
      revision_required_reason
      created_date
      closed_date
    }
  }
}
"""

SUBMIT_ORDER_MUTATION = """
mutation submitOrder($input: SubmitOrderInput) {
  submitOrder(input: $input) {
    status
    status_details {
      open
      pending
      accepted
      declined
      cancelled
      submitted
      revision_required
      completed
      resubmitted
      resubmission_accepted
      preorder
      cancellation_reason
      cancelled_by
      revision_required_reason
      created_date
      closed_date
    }
  }
}
"""

SEND_MESSAGE_MUTATION = """
mutation sendMessage($input: MessageInput) {
  sendMessage(input: $input) {
    success
  }
}
"""

ADD_FILE_MUTATION = """
mutation addFiles($input: AddFilesInput) {
  addFiles(input: $input) {
    outstanding_tasks
  }
}
"""

REMOVE_FILE_MUTATION = """
mutation removeFiles($input: RemoveFilesInput) {
  removeFiles(input: $input) {
    order {
      primary_document {
        _id
        name
        url
        tag
      }
      additional_documents {
        _id
        name
        url
        tag
      }
      customer_files {
        _id
        name
        url
        tag
      }
    }
    outstanding_tasks
  }
}
"""


FULL_FILL_TITLE_SEARCH_MUTATION = """
mutation fulfillTitleSearchPlus($input: TitleSearchPlusInput) {
  fulfillTitleSearchPlus(input: $input) {
    outstanding_tasks
  }
}
"""
