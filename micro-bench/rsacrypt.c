/**
 */
#include <stdio.h>
#include <string.h>
#include <openssl/rsa.h>
#include <openssl/sha.h>
#include <openssl/objects.h>
#include <openssl/pem.h>
#include <openssl/err.h>

// 3072, 7680, 15360

#define PRIVATE_KEY_FILE  "RSAPriKey_3072.pem"
#define PUBLIC_KEY_FILE   "RSAPubKey_3072.pub"

typedef unsigned char byte;

uint64_t rdtsc(){
    unsigned int lo,hi;
    __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
    return ((uint64_t)hi << 32) | lo;
}

// fill byte stram with random content. not cryptographic strong random
void fill_with_random(unsigned char *stream, int n)
{
    size_t i;
    for (i = 0; i < n; i++)
    {
      stream[i] = (unsigned char) (rand() % 255 + 1);
    }
    stream[n] = 0;
}

// note that the only 0 can show up at the end of the stream
char* gen_random_bytestream(int num_bytes)
{
  unsigned char* stream=malloc(num_bytes + 1);
  if (stream == NULL)
    {
        printf("ERROR : Could not allocate memory for random buffer !");
    }
    fill_with_random(stream, num_bytes);
  return stream;
}

static void
printHex(const char *title, const unsigned char *s, int len)
{
	int     n;
	printf("%s:", title);
	for (n = 0; n < len; ++n) {
		if ((n % 16) == 0) {
			printf("\n%04x", n);
		}
		printf(" %02x", s[n]);
	}
	printf("\n");
}

void handleErrors(void)
{
  ERR_print_errors_fp(stderr);
  abort();
}

void generate_pri_keys()
{
  // 3072, 7680, 15360
	FILE   *priKeyFile;
  RSA *prikey=NULL;

	prikey = RSA_generate_key(15360, RSA_F4, NULL, NULL);
	if (prikey == NULL) {
		printf("RSA_generate_key: error\n");
    return;
	}
	priKeyFile = fopen("RSAPriKey_15360.pem", "w");
	if (priKeyFile == NULL)	{
		perror("failed to fopen");
    return;
	}
  PEM_write_RSAPrivateKey(priKeyFile, prikey, NULL, NULL, 0, NULL, NULL);
}

int main(int argc, char *argv[]) {
  OpenSSL_add_all_algorithms();
  ERR_load_crypto_strings();

  // load private and public keys
  RSA *prikey=NULL, *pubkey=NULL;
  FILE *f_pri;
  if(NULL != (f_pri= fopen(PRIVATE_KEY_FILE, "r")) ) {
    prikey = PEM_read_RSAPrivateKey(f_pri, NULL, NULL, NULL);
    printf("Loaded Private key ... \n");
  }
  FILE * f_pub;
  if(NULL != (f_pub= fopen(PUBLIC_KEY_FILE, "r")) ) {
    pubkey = PEM_read_RSA_PUBKEY(f_pub, NULL, NULL, NULL);
    printf("Loaded Public key ... \n");
  }

  // becnhamrk
  uint64_t    start_cycles, end_cycles, total_cycles, cycles_avg;
  uint64_t    start_cycles_ve, end_cycles_ve, total_cycles_ve, cycles_avg_ve;
  int repetitions = 3;
  for(int data_size_kb=512; data_size_kb<=64 * 1024; data_size_kb+=512) {

      int data_size = 1024 * data_size_kb;
      byte *msg = gen_random_bytestream(data_size);
      int msg_len = strlen ((byte *)msg);

      unsigned char hash[SHA512_DIGEST_LENGTH];
      int     ret;
      SHA512(msg, msg_len, hash);

      total_cycles = 0;
      total_cycles_ve = 0;

      for(int r=0; r<repetitions; r++) {
        unsigned char sign[512];
        unsigned int signLen;

          start_cycles = rdtsc();
          RSA_sign(NID_sha512, hash, SHA512_DIGEST_LENGTH, sign,
        				   &signLen, prikey);
          end_cycles = rdtsc();
          total_cycles += (end_cycles - start_cycles);

          start_cycles_ve = rdtsc();
          RSA_verify(NID_sha512, hash, SHA512_DIGEST_LENGTH, sign,
        					 signLen, pubkey);
          end_cycles_ve = rdtsc();
          total_cycles_ve += (end_cycles_ve - start_cycles_ve);
      }
      double avg_cycles = (double)total_cycles/repetitions;
      double avg_cycles_ve = (double)total_cycles_ve/repetitions;
      printf("%8f\n", avg_cycles_ve);
  }

	RSA_free(prikey);
	RSA_free(pubkey);

  return 0;
}
