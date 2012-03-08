//
//  STMetadataView.h
//  Stamped
//
//  Created by Landon Judkins on 3/8/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STMetadata.h"

@interface STMetadataView : UIView

- (id)initWithMetadata:(id<STMetadata>)metadata;

@end
