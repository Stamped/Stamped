//
//  EntityDetailViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/9/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <RestKit/RestKit.h>
#import "UIColor+Stamped.h"
#import "STImageView.h"
#import "ShowImageViewController.h"
#import "STViewController.h"
#import "Util.h"
#import "STEntityDetail.h"
#import "STViewDelegate.h"
#import "STSynchronousWrapper.h"
#import "STStandardViewController.h"
#import "STContainerViewController.h"

@class Stamp;

@interface EntityDetailViewController : STContainerViewController

- (id)initWithEntityID:(NSString*)entityID;
- (id)initWithEntityObject:(Entity*)entity;
- (id)initWithSearchResult:(SearchResult*)searchResult;

@property (nonatomic, retain) Stamp* referringStamp;
@property (nonatomic, readonly) id<STEntityDetail> entityDetail;
@property (nonatomic, readonly) NSOperationQueue* operationQueue;
@property (nonatomic, retain) STSynchronousWrapper* synchronousWrapper;

@property (nonatomic, retain) IBOutlet UIActivityIndicatorView* loadingView;


@end
