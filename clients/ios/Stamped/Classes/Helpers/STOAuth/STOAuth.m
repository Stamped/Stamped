//
//  STOAuth.m
//  STOAuth
//
//  Created by Devin Doty on 11/25/11.
//  Copyright (c) 2011 __MyCompanyName__. All rights reserved.
//

#import "STOAuth.h"
#import "NSData+Base64.h"
#import <CommonCrypto/CommonHMAC.h>


@implementation STOAuth

+ (NSString*)MD5Hash:(NSString*)string {
    const char *concat_str = [string UTF8String];
    unsigned char result[CC_MD5_DIGEST_LENGTH];
    CC_MD5(concat_str, strlen(concat_str), result);
    NSMutableString *hash = [NSMutableString string];
    for (int i = 0; i < 16; i++)
        [hash appendFormat:@"%02X", result[i]];
    return [hash lowercaseString];
}

+ (NSString *)paramStringForParams:(NSArray *)params joiner:(NSString *)joiner shouldQuote:(BOOL)shouldQuote shouldSort:(BOOL)shouldSort {
    // create a string by joining the supplied param objects
    
    if (shouldSort) {
        // sort params by name and value
        NSArray *descs = [STOAuthParameter sortDescriptors];
        params = [params sortedArrayUsingDescriptors:descs];
    }
    
    // make an array of the encoded name=value items
    NSArray *encodedArray;
    if (shouldQuote) {
        encodedArray = [params valueForKey:@"quotedEncodedParam"];
    } else {
        encodedArray = [params valueForKey:@"encodedParam"];
    }
    
    // join the items
    NSString *result = [encodedArray componentsJoinedByString:joiner];
    return result;
}

+ (void)addParamValue:(id)value forName:(id)name toArray:(NSMutableArray*)array {
    
    [array addObject:[STOAuthParameter parameterWithName:name value:value]];
    
}

+ (NSString *)encodedSTOAuthParameterForString:(NSString *)str {
    // http://oauth.net/core/1.0a/#encoding_parameters
    
    CFStringRef originalString = (CFStringRef) str;
    
    CFStringRef leaveUnescaped = CFSTR("ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                                       "abcdefghijklmnopqrstuvwxyz"
                                       "-._~");
    CFStringRef forceEscaped =  CFSTR("%!$&'()*+,/:;=?@");
    
    CFStringRef escapedStr = NULL;
    if (str) {
        escapedStr = CFURLCreateStringByAddingPercentEscapes(kCFAllocatorDefault, originalString, leaveUnescaped, forceEscaped, kCFStringEncodingUTF8);
        //CFBridgingRelease(escapedStr);
    }
    
    return (NSString *)escapedStr;
}

+ (NSString *)stringWithBase64ForData:(NSData *)data {
    // Cyrus Najmabadi elegent little encoder from
    // http://www.cocoadev.com/index.pl?BaseSixtyFour
    if (data == nil) return nil;
    
    const uint8_t* input = [data bytes];
    NSUInteger length = [data length];
    
    NSUInteger bufferSize = ((length + 2) / 3) * 4;
    NSMutableData* buffer = [NSMutableData dataWithLength:bufferSize];
    
    uint8_t* output = [buffer mutableBytes];
    
    static char table[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    
    for (NSUInteger i = 0; i < length; i += 3) {
        NSInteger value = 0;
        for (NSUInteger j = i; j < (i + 3); j++) {
            value <<= 8;
            
            if (j < length) {
                value |= (0xFF & input[j]);
            }
        }
        
        NSInteger idx = (i / 3) * 4;
        output[idx + 0] =                    table[(value >> 18) & 0x3F];
        output[idx + 1] =                    table[(value >> 12) & 0x3F];
        output[idx + 2] = (i + 1) < length ? table[(value >> 6)  & 0x3F] : '=';
        output[idx + 3] = (i + 2) < length ? table[(value >> 0)  & 0x3F] : '=';
    }
    
    NSString *result = [[NSString alloc] initWithData:buffer encoding:NSASCIIStringEncoding];
    return result;
}

+ (NSString *)signatureWithBaseString:(NSString*)baseString secret:(NSString*)secret {
    
    NSData * secretData = [secret dataUsingEncoding:NSUTF8StringEncoding];
    NSData * baseData = [baseString dataUsingEncoding:NSUTF8StringEncoding];
    
    //uint8_t digest[CC_SHA1_DIGEST_LENGTH] = {0};
    uint8_t digest[20] = {0};
    CCHmac(kCCHmacAlgSHA1, secretData.bytes, secretData.length,
           baseData.bytes, baseData.length, digest);
    //NSData * signatureData = [NSData dataWithBytes:digest length:CC_SHA256_DIGEST_LENGTH];
    NSData * signatureData = [NSData dataWithBytes:digest length:20];
    return [signatureData base64EncodedString];
}

+ (NSString *)signClearText:(NSString *)string withSecret:(NSString *)secret {
    
    CCHmacContext context;
    const char    *keyCString = [secret cStringUsingEncoding:NSASCIIStringEncoding];
    NSData *data = [string dataUsingEncoding:NSASCIIStringEncoding];
    
    CCHmacInit(&context, kCCHmacAlgSHA1, keyCString, strlen(keyCString));
    CCHmacUpdate(&context, [data bytes], [data length]);
    
    unsigned char digestRaw[CC_SHA256_DIGEST_LENGTH];
    
    int digestLength;
    digestLength = CC_SHA1_DIGEST_LENGTH;
    
    CCHmacFinal(&context, digestRaw);
    
    NSData *digestData = [NSData dataWithBytes:digestRaw length:digestLength];
    
    return [NSString stringWithFormat:@"%@", [digestData base64EncodedString]]; 
}

+ (NSString *)timestamp {
    
    NSTimeInterval timeInterval = [[NSDate date] timeIntervalSince1970];
    unsigned long long timestampVal = (unsigned long long) timeInterval;
    NSString *timestamp = [NSString stringWithFormat:@"%qu", timestampVal];
    return timestamp;
}

+ (NSString *)nonce {
    
    // random 64-bit number
    unsigned long long nonceVal = ((unsigned long long) arc4random()) << 32 | (unsigned long long) arc4random();
    NSString *nonce = [NSString stringWithFormat:@"%qu", nonceVal];
    return nonce;
}

+ (NSString *)normalizedRequestURLStringForRequest:(EGOHTTPRequest *)request {
    // http://oauth.net/core/1.0a/#anchor13
    
    NSURL *url = [[request URL] absoluteURL];
    
    NSString *scheme = [[url scheme] lowercaseString];
    NSString *host = [[url host] lowercaseString];
    int port = [[url port] intValue];
    
    // NSURL's path method has an unfortunate side-effect of unescaping the path,
    // but CFURLCopyPath does not
    CFStringRef cfPath = CFURLCopyPath((CFURLRef)url);
    __autoreleasing NSString *path = CFBridgingRelease(cfPath);
    
    // include only non-standard ports for http or https
    NSString *portStr;
    if (port == 0
        || ([scheme isEqual:@"http"] && port == 80)
        || ([scheme isEqual:@"https"] && port == 443)) {
        portStr = @"";
    } else {
        portStr = [NSString stringWithFormat:@":%u", port];
    }
    
    if ([path length] == 0) {
        path = @"/";
    }
    
    NSString *result = [NSString stringWithFormat:@"%@://%@%@%@",
                        scheme, host, portStr, path];
    return result;
}

+ (NSString *)signatureForParams:(NSMutableArray *)params request:(EGOHTTPRequest *)request token:(NSString*)token {
    // construct signature base string per
    // http://oauth.net/core/1.0a/#signing_process
    NSString *requestURLStr = [self normalizedRequestURLStringForRequest:request];
    NSString *method = [[request requestMethod] uppercaseString];
    if ([method length] == 0) {
        method = @"GET";
    }
        
    // the signature params exclude the signature
    NSMutableArray *signatureParams = [NSMutableArray arrayWithArray:params];
    
    // add request query parameters
    //[[self class] addQueryFromRequest:request toParams:signatureParams];
    
    // add parameters from the POST body, if any
    //[[self class] addBodyFromRequest:request toParams:signatureParams];
    
    NSString *paramStr = [STOAuth paramStringForParams:signatureParams joiner:@"&" shouldQuote:NO shouldSort:YES];
    
    // the base string includes the method, normalized request URL, and params
    NSString *requestURLStrEnc = [STOAuth encodedSTOAuthParameterForString:requestURLStr];
    NSString *paramStrEnc = [STOAuth encodedSTOAuthParameterForString:paramStr];
    
    NSString *sigBaseString = [NSString stringWithFormat:@"%@&%@&%@", method, requestURLStrEnc, paramStrEnc];
        
    NSLog(@"%@", sigBaseString);
    return [STOAuth signatureWithBaseString:sigBaseString secret:token];
}


@end

@implementation STOAuthParameter

@synthesize name = name_;
@synthesize value = value_;

+ (STOAuthParameter *)parameterWithName:(NSString *)name value:(NSString *)value {
    STOAuthParameter *obj = [[self alloc] init] ;
    [obj setName:name];
    [obj setValue:value];
    return obj;
}

- (void)dealloc {
    name_=nil;
    value_=nil;
    [super dealloc];
}

- (NSString *)encodedValue {
    NSString *value = [self value];
    NSString *result = [STOAuth encodedSTOAuthParameterForString:value];
    return result;
}

- (NSString *)encodedName {
    NSString *name = [self name];
    NSString *result = [STOAuth encodedSTOAuthParameterForString:name];
    return result;
}

- (NSString *)encodedParam {
    NSString *str = [NSString stringWithFormat:@"%@=%@", [self encodedName], [self encodedValue]];
    return str;
}

- (NSString *)quotedEncodedParam {
    NSString *str = [NSString stringWithFormat:@"%@=\"%@\"", [self encodedName], [self encodedValue]];
    return str;
}

- (NSString *)description {
    return [self encodedParam];
}

+ (NSArray *)sortDescriptors {
    // sort by name and value
    SEL sel = @selector(compare:);
    
    NSSortDescriptor *desc1, *desc2;
    desc1 = [[NSSortDescriptor alloc] initWithKey:@"name" ascending:YES selector:sel];
    desc2 = [[NSSortDescriptor alloc] initWithKey:@"encodedValue" ascending:YES selector:sel];
    
    return [NSArray arrayWithObjects:desc1, desc2, nil];
}

@end