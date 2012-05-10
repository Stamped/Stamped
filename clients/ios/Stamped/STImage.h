//
//  STImage.h
//  Stamped
//
//  Created by Landon Judkins on 4/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STImage <NSObject>

@property (nonatomic, readonly, copy) NSString* url;
@property (nonatomic, readonly, copy) NSNumber* width;
@property (nonatomic, readonly, copy) NSNumber* height;
@property (nonatomic, readonly, copy) NSString* source;
@property (nonatomic, readonly, copy) NSString* filter;

@end
