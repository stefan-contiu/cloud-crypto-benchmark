/**
 */
#include <stdio.h>
#include <string.h>
#include <openssl/sha.h>
#include <openssl/objects.h>
#include <openssl/pem.h>
#include <openssl/err.h>
#include <openssl/ecdsa.h>
#include <time.h>

// 3072, 7680, 15360

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

int main(int argc, char *argv[]) {
  OpenSSL_add_all_algorithms();
  ERR_load_crypto_strings();

  int        ret;
  EC_KEY    *eckey = EC_KEY_new();
  //EC_GROUP *group;

// NID_secp224r1, NID_secp384r1, NID_secp521r1


  eckey = EC_KEY_new_by_curve_name(NID_secp521r1);
  EC_KEY_generate_key(eckey);

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


/*
        clock_t begin = clock();

        ECDSA_sign(NID_sha512, hash, SHA512_DIGEST_LENGTH, sign,
                 &signLen, eckey);

        clock_t end = clock();
        total_cycles = (double)(end - begin) / CLOCKS_PER_SEC;
*/


          start_cycles = rdtsc();
          ECDSA_sign(NID_sha512, hash, SHA512_DIGEST_LENGTH, sign,
        				   &signLen, eckey);
          end_cycles = rdtsc();
          total_cycles += (end_cycles - start_cycles);

          start_cycles_ve = rdtsc();
          ECDSA_verify(NID_sha512, hash, SHA512_DIGEST_LENGTH, sign,
        					 signLen, eckey);
          end_cycles_ve = rdtsc();
          total_cycles_ve += (end_cycles_ve - start_cycles_ve);
      }
      double avg_cycles = (double)total_cycles/repetitions;
      double avg_cycles_ve = (double)total_cycles_ve/repetitions;
      printf("%8f\n", avg_cycles_ve);
  }

  return 0;
}
