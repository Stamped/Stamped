//
//  STSimpleStampPreview.h
//  Stamped
//
//  Created by Landon Judkins on 5/31/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STStampPreview.h"
#import "STStamp.h"

@interface STSimpleStampPreview : NSObject <STStampPreview, NSCoding>

@property (nonatomic, readwrite, copy) NSString* stampID;
@property (nonatomic, readwrite, retain) id<STUser> user;

+ (RKObjectMapping*)mapping;

+ (STSimpleStampPreview*)stampPreviewFromStamp:(id<STStamp>)stamp;

@end
