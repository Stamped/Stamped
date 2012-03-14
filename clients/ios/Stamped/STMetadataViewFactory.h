//
//  STMetadataViewFactory.h
//  Stamped
//
//  Created by Landon Judkins on 3/14/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STEntityDetail.h"
#import "STViewDelegate.h"

@interface STMetadataViewFactory : NSObject

- (void)createWithEntityDetail:(id<STEntityDetail>)entity
                      delegate:(id<STViewDelegate>)delegate
                     withLabel:(id)label;
@end
