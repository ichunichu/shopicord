from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment


# Creating Access Token for Sandbox
client_id = "AX-MhxuCqRXIuozIHgS87GRRkryln2zhYMQh_y8gozhW4xr9p8yNfF3SkrRowqGKaqoKlpP1hzIzM4_j"
client_secret = "EFYT2vOnBlqEAxbpN-kdKW1j-iFcVwA_n12Kl8kiB_4SOdRPDSwTllV8GGUyP0QcW6RZjzr8SRXmIiAu"
# Creating an environment
environment = SandboxEnvironment(client_id=client_id, client_secret=client_secret)
client = PayPalHttpClient(environment)

from sample.CaptureIntentExamples import CreateOrder
from sample.CaptureIntentExamples import CaptureOrder
orderer = CreateOrder()

order = orderer.create_order()
print(order.result.dict())
input("checkout")
print(CaptureOrder().capture_order(order.result.dict()["id"]).result.dict())
print(CaptureOrder().capture_order("97U399434G505902C").result.dict())

