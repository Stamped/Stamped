//
//  StampDetailViewController.h
//  Stamped
//
//  Created by Kevin Palms on 2/6/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>
#import <CoreData/CoreData.h>


@interface StampDetailViewController : UIViewController <UIScrollViewDelegate, UIActionSheetDelegate> {
	NSNumber				*stampId;
	UIToolbar				*toolbar;
	UIBarButtonItem			*starButton;
}

- (id)initInManagedObjectContext:(NSManagedObjectContext *)context;

@property (retain) NSNumber *stampId;
@property (nonatomic, retain) UIToolbar	*toolbar;

@end
