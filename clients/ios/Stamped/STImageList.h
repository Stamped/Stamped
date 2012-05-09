//
//  STImageList.h
//  Stamped
//
//  Created by Landon Judkins on 5/9/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STImage.h"
#import "STAction.h"

@protocol STImageList <NSObject>

@property (nonatomic, readonly, copy) NSArray<STImage>* sizes;
@property (nonatomic, readonly, copy) NSString* caption;
@property (nonatomic, readonly, retain) id<STAction> action;

@end
