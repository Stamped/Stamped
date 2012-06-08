//
//  STS3Uploader.h
//  Stamped
//
//  Created by Devin Doty on 6/8/12.
//
//

#import <Foundation/Foundation.h>

typedef void(^STS3UploaderProgress)(float progress);
typedef void(^STS3UploaderCompletion)(NSString *, BOOL);

@class ASIS3ObjectRequest;
@interface STS3Uploader : NSObject

@property(nonatomic,readonly,retain) ASIS3ObjectRequest *request;
@property(nonatomic,retain) NSString *filePath;
@property(nonatomic,readonly,getter = isUploading) BOOL uploading;
@property(nonatomic,readonly) float progress;

- (void)startWithProgress:(STS3UploaderProgress)progress completion:(STS3UploaderCompletion)completion;
- (void)cancel;

@end
