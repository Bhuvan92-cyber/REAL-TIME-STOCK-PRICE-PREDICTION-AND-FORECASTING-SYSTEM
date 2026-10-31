# Payment provider integration

`PaymentProvider` defines checkout, subscription lookup, cancellation, and
webhook verification. `BillingDisabledProvider` is the active default and
always fails clearly; it never grants paid access. A future adapter must verify
provider signatures and update subscriptions only from idempotent webhook
events.
