//
//  DetailAViewController.h
//  StampedMockB
//
//  Created by Kevin Palms on 6/29/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>
#import <QuartzCore/QuartzCore.h>


@interface DetailAViewController : UIViewController {
  NSManagedObjectID *stampID;
}

- (id)initInManagedObjectContext:(NSManagedObjectContext *)context;

@property (retain) NSManagedObjectID *stampID;

@end
