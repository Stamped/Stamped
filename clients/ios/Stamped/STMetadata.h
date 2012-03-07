//
//  STMetadata.h
//  Stamped
//
//  Created by Landon Judkins on 3/6/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STMetadataItem

@protocol STMetadata <NSObject>

@property (nonatomic, readonly, assign) NSInteger name;
@property (nonatomic, readonly, retain) NSArray<STMetadataItem>* data;

@end
