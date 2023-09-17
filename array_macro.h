//#include <stdint.h>
//#include <memory.h>
//#include <malloc.h>

#define aALLOC(T,v,s)       array_##T##_alloc(v,s)
#define aREALLOC(T,v,s)     array_##T##_realloc(v,s)
#define aDEALLOC(T,v)       array_##T##_dealloc(v)
#define aCOPY(T,dst,src) array_##T##_copy(dst,src)
#define aMOVE(T,dst,src) array_##T##_move(dst,src)


//#define array(T) array_##T
//#define array_dealloc_attrib(T) __attribute__((cleanup(array_##T##_dealloc)))
//#define ARRAY_FUNCTION_PREFIX __attribute__((always_inline)) inline

#define ARRAY_DEFINE(T)\
typedef struct array_##T{\
 T* ptr;\
 uint64_t size;\
} array_##T;\
\
\
ARRAY_FUNCTION_PREFIX T* const array_##T##_elm(array_##T* a,uint64_t i)\
{return &a->ptr[i];}\
\
ARRAY_FUNCTION_PREFIX void array_##T##_alloc(array_##T* a,uint64_t size){\
  if(size == 0) a->ptr = NULL;\
  else a->ptr = (T*)calloc(size,sizeof(T));\
  a->size = size;\
}\
\
ARRAY_FUNCTION_PREFIX void array_##T##_dealloc(array_##T* a){\
  if(a->ptr){free(a->ptr); a->ptr = NULL;}\
  a->size = 0;\
}\
\
ARRAY_FUNCTION_PREFIX void array_##T##_realloc(array_##T* a,uint64_t size){\
  if(a->ptr && a->size > 0 && a->size != size) {a->ptr = (T*)realloc(a->ptr,size*sizeof(T)); a->size = size;}\
  else aALLOC(T,a,size);\
}\
\
ARRAY_FUNCTION_PREFIX void array_##T##_copy(array_##T* dst,array_##T* src){\
  dst->size = src->size;\
  aREALLOC(T, dst, src->size);\
  memcpy(dst->ptr, src->ptr, src->size * sizeof(T));\
}\
\
ARRAY_FUNCTION_PREFIX void array_##T##_move(array_##T* dst,array_##T* src){\
  dst->size = src->size;\
  dst->ptr = src->ptr;\
  \
  src->ptr = NULL;\
  src->size = 0;\
}\
\
ARRAY_FUNCTION_PREFIX void array_##T##_clear(array_##T* a){\
  memset(a->ptr, 0, a->size*sizeof(T));\
}\
