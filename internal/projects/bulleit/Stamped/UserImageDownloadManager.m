//
//  UserImageDownloadManager.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/7/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "UserImageDownloadManager.h"

#import <CommonCrypto/CommonDigest.h>

static UserImageDownloadManager* sharedUserImageDownloadManager_ = nil;
static const CGFloat kMediumImageSize = 41.0;
static UIImage* cachedMediumPlaceholder_ = nil;
static UIImage* cachedPlaceHolder_ = nil;

NSString* const kUserImageLoadedNotification = @"kUserImageLoadedNotification";
NSString* const kMediumUserImageLoadedNotification = @"kMediumUserImageLoadedNotification";

@interface UserImageDownloader : NSObject

- (void)start;
- (void)cancel;

@property (nonatomic, retain) id<UserImageDownloaderDelegate> delegate;
@property (nonatomic, copy) NSString* imageURL;
@property (nonatomic, retain) NSMutableData* downloadData;
@property (nonatomic, retain) NSURLConnection* connection;
@property (nonatomic, readonly) BOOL active;

@end

@implementation UserImageDownloader

@synthesize connection = connection_;
@synthesize downloadData = downloadData_;
@synthesize imageURL = imageURL_;
@synthesize delegate = delegate_;
@synthesize active = active_;

- (void)start {
  self.downloadData = [NSMutableData data];
  NSURLRequest* request = [NSURLRequest requestWithURL:[NSURL URLWithString:imageURL_]];
  NSURLConnection* connection = [[NSURLConnection alloc] initWithRequest:request
                                                                delegate:self];
  self.connection = connection;
  [connection release];
  active_ = YES;
}

- (void)cancel {
  [self.connection cancel];
  self.connection = nil;
  self.downloadData = nil;
  self.imageURL = nil;
  active_ = NO;
}

- (void)dealloc {
  active_ = NO;
  self.delegate = nil;
  self.connection = nil;
  self.downloadData = nil;
  self.imageURL = nil;
  [super dealloc];
}

#pragma mark - NSURLConnectionDelegate methods.

- (void)connection:(NSURLConnection*)connection didReceiveData:(NSData*)data {
  [self.downloadData appendData:data];
}

- (void)connection:(NSURLConnection*)connection didFailWithError:(NSError*)error {
  self.downloadData = nil;
  self.connection = nil;
  active_ = NO;
}

- (void)connectionDidFinishLoading:(NSURLConnection*)connection {
  UIImage* img = [[[UIImage alloc] initWithData:self.downloadData] autorelease];
  self.downloadData = nil;
  self.connection = nil;
  [delegate_ userImageDidLoad:img fromURL:imageURL_];
  active_ = NO;
}

@end


@implementation UserImageDownloadManager

+ (UserImageDownloadManager*)sharedManager {
  if (sharedUserImageDownloadManager_ == nil)
    sharedUserImageDownloadManager_ = [[super allocWithZone:NULL] init];

  return sharedUserImageDownloadManager_;
}

+ (NSString*)SHA1DigestFromString:(NSString*)input {
  const char* c_str = [input cStringUsingEncoding:NSUTF8StringEncoding];
  NSData* data = [NSData dataWithBytes:c_str length:input.length];
  uint8_t digest[CC_SHA1_DIGEST_LENGTH];
  CC_SHA1(data.bytes, data.length, digest);

  NSMutableString* output = [NSMutableString stringWithCapacity:CC_SHA1_DIGEST_LENGTH * 2];
  for (int i = 0; i < CC_SHA1_DIGEST_LENGTH; ++i)
    [output appendFormat:@"%02x", digest[i]];

  return output;  
}

+ (id)allocWithZone:(NSZone*)zone {
  return [[self sharedManager] retain];
}

- (id)copyWithZone:(NSZone*)zone {
  return self;
}

- (id)retain {
  return self;
}

- (NSUInteger)retainCount {
  return NSUIntegerMax;
}

- (oneway void)release {
  // Do nothin'.
}

- (id)autorelease {
  return self;
}

#pragma mark - Begin custom implementation.

- (UIImage*)generateMediumProfileImage:(UIImage*)image {
  CGFloat width = kMediumImageSize + 4;
  CGFloat height = kMediumImageSize + 4;
  UIGraphicsBeginImageContextWithOptions(CGSizeMake(width, height), NO, 0.0);
  CGContextRef imgContext = UIGraphicsGetCurrentContext();
  CGContextTranslateCTM(imgContext, 0, height);
  CGContextScaleCTM(imgContext, 1.0, -1.0);
  CGRect imgFrame = CGRectMake(0, 0, width, height);
  CGContextSaveGState(imgContext);
  UIBezierPath* clearBorderPath = [UIBezierPath bezierPathWithRect:imgFrame];
  CGContextSetFillColorWithColor(imgContext, [UIColor clearColor].CGColor);
  CGContextAddPath(imgContext, clearBorderPath.CGPath);
  CGContextClosePath(imgContext);
  CGContextFillPath(imgContext);
  CGContextRestoreGState(imgContext);
  CGContextSaveGState(imgContext);
  UIBezierPath* path = [UIBezierPath bezierPathWithRect:CGRectInset(imgFrame, 2, 2)];
  CGContextSetFillColorWithColor(imgContext, [UIColor whiteColor].CGColor);
  CGContextAddPath(imgContext, path.CGPath);
  CGContextClosePath(imgContext);
  CGContextFillPath(imgContext);
  CGContextRestoreGState(imgContext);
  CGContextDrawImage(imgContext, CGRectInset(imgFrame, 4, 4), image.CGImage);
  UIImage* userImage = UIGraphicsGetImageFromCurrentImageContext();
  UIGraphicsEndImageContext();
  return userImage;
}

- (NSURL*)documentsDirectory {
  return [[[NSFileManager defaultManager] URLsForDirectory:NSDocumentDirectory inDomains:NSUserDomainMask] lastObject];
}

- (NSString*)mediumImagePathWithImageURL:(NSString*)imageURL {
  NSURL* fullPath = [[self documentsDirectory] URLByAppendingPathComponent:
      [NSString stringWithFormat:@"user_%@_medium.png",
          [UserImageDownloadManager SHA1DigestFromString:imageURL]]];
  return [fullPath path];
}

- (NSString*)imagePathWithImageURL:(NSString*)imageURL {
  NSURL* fullPath = [[self documentsDirectory] URLByAppendingPathComponent:
      [NSString stringWithFormat:@"user_%@_regular.png",
          [UserImageDownloadManager SHA1DigestFromString:imageURL]]];
  return [fullPath path];
}

- (void)downloadImageAtURL:(NSString*)imageURL {
  if (!downloads_)
    downloads_ = [[NSMutableDictionary alloc] initWithCapacity:5];

  UserImageDownloader* downloader = [downloads_ objectForKey:imageURL];
  if (downloader) {
    if (!downloader.active)
      [downloader start];
  
    return;
  }
  downloader = [[UserImageDownloader alloc] init];
  downloader.imageURL = imageURL;
  downloader.delegate = self;
  [downloads_ setObject:downloader forKey:imageURL];
  [downloader start];
  [downloader release];
}

- (UIImage*)mediumProfileImageAtURL:(NSString*)imageURL {
  // Check the cache first.
  UIImage* img = nil;
  if (mediumImageCache_)
    img = [mediumImageCache_ objectForKey:imageURL];
  
  if (!img)
    img = [UIImage imageWithContentsOfFile:[self mediumImagePathWithImageURL:imageURL]];

  if (img) {
    if (!mediumImageCache_)
      mediumImageCache_ = [[NSMutableDictionary alloc] initWithCapacity:5];
    
    [mediumImageCache_ setObject:img forKey:imageURL];
    return img;
  }

  [self downloadImageAtURL:imageURL];

  if (!cachedMediumPlaceholder_) {
    cachedMediumPlaceholder_ = [[self generateMediumProfileImage:[UIImage imageNamed:@"profile_placeholder"]] retain];
  }
  return cachedMediumPlaceholder_;
}

- (UIImage*)profileImageAtURL:(NSString*)imageURL {
  UIImage* img = nil;
  if (imageCache_)
    img = [imageCache_ objectForKey:imageURL];
  
  if (!img)
    img = [UIImage imageWithContentsOfFile:[self imagePathWithImageURL:imageURL]];
  
  if (img) {
    if (!imageCache_)
      imageCache_ = [[NSMutableDictionary alloc] initWithCapacity:5];
    
    [imageCache_ setObject:img forKey:imageURL];
    return img;
  }

  [self downloadImageAtURL:imageURL];

  if (!cachedPlaceHolder_)
    cachedPlaceHolder_ = [[UIImage imageNamed:@"profile_placeholder"] retain];
  
  return cachedPlaceHolder_;
}

#pragma mark - UserImageDownloaderDelegate methods.

- (void)userImageDidLoad:(UIImage*)image fromURL:(NSString*)imageURL {
  if (!image || !imageURL)
    return;

  UIImage* scaledImage = [self generateMediumProfileImage:image];
  [UIImagePNGRepresentation(scaledImage)
       writeToFile:[self mediumImagePathWithImageURL:imageURL] 
        atomically:YES];
  if (!mediumImageCache_)
    mediumImageCache_ = [[NSMutableDictionary alloc] initWithCapacity:5];

  [mediumImageCache_ setObject:scaledImage forKey:imageURL];
  [[NSNotificationCenter defaultCenter]
      postNotificationName:kMediumUserImageLoadedNotification object:imageURL];

  [UIImagePNGRepresentation(image)
      writeToFile:[self imagePathWithImageURL:imageURL] 
       atomically:YES];
  if (!imageCache_)
    imageCache_ = [[NSMutableDictionary alloc] initWithCapacity:5];
  
  [imageCache_ setObject:image forKey:imageURL];
  [[NSNotificationCenter defaultCenter]
      postNotificationName:kUserImageLoadedNotification object:imageURL];
  [downloads_ removeObjectForKey:imageURL];
}

@end
